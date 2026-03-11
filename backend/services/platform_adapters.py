"""
Platform Adapters — Real API delivery logic for each platform.
Each adapter: authenticate, upload/post content, return result dict.
Content is served via the app's own URL (APP_BASE_URL).
"""

import os
import json
import httpx
import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

TIMEOUT = httpx.Timeout(60.0, connect=15.0)


def get_app_base_url() -> str:
    """Get the public base URL for the app used in content delivery."""
    return os.environ.get("APP_BASE_URL", os.environ.get("FRONTEND_URL", "")).rstrip("/")


class DeliveryResult:
    """Standard result from a platform delivery attempt."""
    def __init__(self, success: bool, platform_content_id: str = "", message: str = "", response_data: dict = None):
        self.success = success
        self.platform_content_id = platform_content_id
        self.message = message
        self.response_data = response_data or {}

    def to_dict(self):
        return {
            "success": self.success,
            "platform_content_id": self.platform_content_id,
            "message": self.message,
            "response_data": self.response_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ─────────────────────────────────────────────
# BASE ADAPTER
# ─────────────────────────────────────────────
class BasePlatformAdapter:
    """Base class for all platform adapters."""
    platform_id: str = ""
    platform_name: str = ""
    required_credentials: list = []

    def validate_credentials(self, credentials: dict) -> bool:
        return all(credentials.get(k) for k in self.required_credentials)

    def get_public_file_url(self, content: dict) -> str:
        """Resolve the public URL for content files using the app's base URL."""
        url = content.get("public_file_url", "")
        if url:
            return url
        file_url = content.get("file_url", "")
        if not file_url:
            return ""
        if file_url.startswith("http"):
            return file_url
        base = get_app_base_url()
        return f"{base}{file_url}" if base else file_url

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        raise NotImplementedError


# ─────────────────────────────────────────────
# YOUTUBE ADAPTER (YouTube Data API v3)
# ─────────────────────────────────────────────
class YouTubeAdapter(BasePlatformAdapter):
    platform_id = "youtube"
    platform_name = "YouTube"
    required_credentials = ["access_token"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing YouTube access_token")

        access_token = credentials["access_token"]
        title = content.get("title", "Untitled")
        description = content.get("description", "")
        tags = content.get("metadata", {}).get("basic", {}).get("tags", [])
        public_url = self.get_public_file_url(content)

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                # Step 1: Initiate resumable upload
                metadata = {
                    "snippet": {
                        "title": title[:100],
                        "description": f"{description[:4900]}\n\nSource: {public_url}" if public_url else description[:5000],
                        "tags": tags[:500] if tags else [],
                        "categoryId": "22",
                    },
                    "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False},
                }

                init_resp = await client.post(
                    "https://www.googleapis.com/upload/youtube/v3/videos",
                    params={"uploadType": "resumable", "part": "snippet,status"},
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json; charset=UTF-8",
                        "X-Upload-Content-Type": "video/*",
                    },
                    content=json.dumps(metadata),
                )

                if init_resp.status_code != 200:
                    return DeliveryResult(False, message=f"YouTube init failed: {init_resp.status_code} {init_resp.text[:200]}")

                upload_url = init_resp.headers.get("Location")
                if not upload_url:
                    return DeliveryResult(False, message="No upload URL returned from YouTube")

                # Step 2: Upload file if available
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    upload_resp = await client.put(
                        upload_url,
                        content=file_bytes,
                        headers={"Content-Type": "video/*"},
                    )
                    if upload_resp.status_code in (200, 201):
                        data = upload_resp.json()
                        return DeliveryResult(
                            True,
                            platform_content_id=data.get("id", ""),
                            message=f"Uploaded to YouTube as {data.get('id')}",
                            response_data={"video_id": data.get("id"), "status": data.get("status", {}), "source_url": public_url},
                        )
                    return DeliveryResult(False, message=f"YouTube upload failed: {upload_resp.status_code}")

                # No file - create metadata-only placeholder with source link
                return DeliveryResult(
                    True,
                    message=f"YouTube upload session initiated (content at: {public_url})" if public_url else "YouTube upload session initiated (no file attached)",
                    response_data={"upload_url": upload_url, "status": "session_created", "source_url": public_url},
                )

        except Exception as e:
            logger.error(f"YouTube delivery error: {e}")
            return DeliveryResult(False, message=f"YouTube error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# TWITTER/X ADAPTER (v2 API)
# ─────────────────────────────────────────────
class TwitterAdapter(BasePlatformAdapter):
    platform_id = "twitter_x"
    platform_name = "Twitter/X"
    required_credentials = ["bearer_token"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        bearer = credentials.get("bearer_token") or credentials.get("access_token")
        if not bearer:
            return DeliveryResult(False, message="Missing Twitter bearer_token or access_token")

        title = content.get("title", "")
        description = content.get("description", "")
        public_url = self.get_public_file_url(content)
        # Include the app URL in the tweet so content is linked back
        text_parts = [title]
        if description:
            text_parts.append(description)
        if public_url:
            text_parts.append(public_url)
        text = "\n\n".join(text_parts)[:280]

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                media_id = None
                # Upload media if file exists
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    # Twitter v1.1 media upload (still required for media)
                    upload_resp = await client.post(
                        "https://upload.twitter.com/1.1/media/upload.json",
                        headers={"Authorization": f"Bearer {bearer}"},
                        files={"media": file_bytes},
                    )
                    if upload_resp.status_code == 200:
                        media_id = upload_resp.json().get("media_id_string")

                # Create tweet
                payload = {"text": text}
                if media_id:
                    payload["media"] = {"media_ids": [media_id]}

                resp = await client.post(
                    "https://api.twitter.com/2/tweets",
                    headers={
                        "Authorization": f"Bearer {bearer}",
                        "Content-Type": "application/json",
                    },
                    content=json.dumps(payload),
                )

                if resp.status_code in (200, 201):
                    data = resp.json().get("data", {})
                    tweet_id = data.get("id", "")
                    return DeliveryResult(
                        True,
                        platform_content_id=tweet_id,
                        message=f"Posted to Twitter/X: {tweet_id}",
                        response_data={**data, "source_url": public_url},
                    )
                return DeliveryResult(False, message=f"Twitter post failed: {resp.status_code} {resp.text[:200]}")

        except Exception as e:
            logger.error(f"Twitter delivery error: {e}")
            return DeliveryResult(False, message=f"Twitter error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# TIKTOK ADAPTER (Content Posting API)
# ─────────────────────────────────────────────
class TikTokAdapter(BasePlatformAdapter):
    platform_id = "tiktok"
    platform_name = "TikTok"
    required_credentials = ["access_token"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing TikTok access_token")

        access_token = credentials["access_token"]
        title = content.get("title", "")[:150]

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                if not file_path or not os.path.exists(file_path):
                    return DeliveryResult(False, message="TikTok requires a video file")

                file_size = os.path.getsize(file_path)

                # Step 1: Initialize upload
                init_resp = await client.post(
                    "https://open.tiktokapis.com/v2/post/publish/video/init/",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    content=json.dumps({
                        "post_info": {"title": title, "privacy_level": "SELF_ONLY"},
                        "source_info": {"source": "FILE_UPLOAD", "video_size": file_size, "chunk_size": file_size},
                    }),
                )

                if init_resp.status_code != 200:
                    return DeliveryResult(False, message=f"TikTok init failed: {init_resp.status_code}")

                data = init_resp.json().get("data", {})
                upload_url = data.get("upload_url")
                publish_id = data.get("publish_id", "")

                if upload_url:
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    upload_resp = await client.put(
                        upload_url,
                        content=file_bytes,
                        headers={
                            "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
                            "Content-Type": "video/mp4",
                        },
                    )
                    if upload_resp.status_code in (200, 201):
                        return DeliveryResult(
                            True,
                            platform_content_id=publish_id,
                            message=f"Uploaded to TikTok: {publish_id}",
                            response_data={"publish_id": publish_id},
                        )
                    return DeliveryResult(False, message=f"TikTok upload failed: {upload_resp.status_code}")

                return DeliveryResult(False, message="No upload URL from TikTok")

        except Exception as e:
            logger.error(f"TikTok delivery error: {e}")
            return DeliveryResult(False, message=f"TikTok error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# SOUNDCLOUD ADAPTER
# ─────────────────────────────────────────────
class SoundCloudAdapter(BasePlatformAdapter):
    platform_id = "soundcloud"
    platform_name = "SoundCloud"
    required_credentials = ["access_token"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing SoundCloud access_token")

        access_token = credentials["access_token"]
        title = content.get("title", "Untitled")
        description = content.get("description", "")
        genre = content.get("metadata", {}).get("basic", {}).get("genre", "")

        try:
            if not file_path or not os.path.exists(file_path):
                return DeliveryResult(False, message="SoundCloud requires an audio file")

            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0)) as client:
                with open(file_path, "rb") as f:
                    resp = await client.post(
                        "https://api.soundcloud.com/tracks",
                        headers={"Authorization": f"OAuth {access_token}"},
                        data={
                            "track[title]": title,
                            "track[description]": description,
                            "track[genre]": genre,
                            "track[sharing]": "private",
                        },
                        files={"track[asset_data]": (os.path.basename(file_path), f)},
                    )

                if resp.status_code in (200, 201):
                    data = resp.json()
                    track_id = str(data.get("id", ""))
                    return DeliveryResult(
                        True,
                        platform_content_id=track_id,
                        message=f"Uploaded to SoundCloud: {track_id}",
                        response_data={"track_id": track_id, "permalink_url": data.get("permalink_url", "")},
                    )
                return DeliveryResult(False, message=f"SoundCloud upload failed: {resp.status_code} {resp.text[:200]}")

        except Exception as e:
            logger.error(f"SoundCloud delivery error: {e}")
            return DeliveryResult(False, message=f"SoundCloud error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# VIMEO ADAPTER
# ─────────────────────────────────────────────
class VimeoAdapter(BasePlatformAdapter):
    platform_id = "vimeo"
    platform_name = "Vimeo"
    required_credentials = ["access_token"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing Vimeo access_token")

        access_token = credentials["access_token"]
        title = content.get("title", "Untitled")
        description = content.get("description", "")

        try:
            if not file_path or not os.path.exists(file_path):
                return DeliveryResult(False, message="Vimeo requires a video file")

            file_size = os.path.getsize(file_path)

            async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0)) as client:
                # Step 1: Create video resource
                create_resp = await client.post(
                    "https://api.vimeo.com/me/videos",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/vnd.vimeo.*+json;version=3.4",
                    },
                    content=json.dumps({
                        "upload": {"approach": "tus", "size": file_size},
                        "name": title,
                        "description": description,
                        "privacy": {"view": "nobody"},
                    }),
                )

                if create_resp.status_code not in (200, 201):
                    return DeliveryResult(False, message=f"Vimeo create failed: {create_resp.status_code}")

                data = create_resp.json()
                upload_link = data.get("upload", {}).get("upload_link")
                video_uri = data.get("uri", "")
                video_id = video_uri.split("/")[-1] if video_uri else ""

                if upload_link:
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    upload_resp = await client.patch(
                        upload_link,
                        content=file_bytes,
                        headers={
                            "Tus-Resumable": "1.0.0",
                            "Upload-Offset": "0",
                            "Content-Type": "application/offset+octet-stream",
                        },
                    )
                    if upload_resp.status_code in (200, 204):
                        return DeliveryResult(
                            True,
                            platform_content_id=video_id,
                            message=f"Uploaded to Vimeo: {video_id}",
                            response_data={"video_id": video_id, "uri": video_uri, "link": data.get("link", "")},
                        )
                    return DeliveryResult(False, message=f"Vimeo upload failed: {upload_resp.status_code}")

                return DeliveryResult(False, message="No upload link from Vimeo")

        except Exception as e:
            logger.error(f"Vimeo delivery error: {e}")
            return DeliveryResult(False, message=f"Vimeo error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# BLUESKY ADAPTER (AT Protocol)
# ─────────────────────────────────────────────
class BlueskyAdapter(BasePlatformAdapter):
    platform_id = "bluesky"
    platform_name = "Bluesky"
    required_credentials = ["handle", "app_password"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing Bluesky handle or app_password")

        handle = credentials["handle"]
        app_password = credentials["app_password"]
        title = content.get("title", "")
        description = content.get("description", "")
        public_url = self.get_public_file_url(content)
        text_parts = [title]
        if description:
            text_parts.append(description)
        if public_url:
            text_parts.append(public_url)
        text = "\n\n".join(text_parts)[:300]

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                # Authenticate
                auth_resp = await client.post(
                    "https://bsky.social/xrpc/com.atproto.server.createSession",
                    content=json.dumps({"identifier": handle, "password": app_password}),
                    headers={"Content-Type": "application/json"},
                )
                if auth_resp.status_code != 200:
                    return DeliveryResult(False, message=f"Bluesky auth failed: {auth_resp.status_code}")

                session = auth_resp.json()
                access_jwt = session["accessJwt"]
                did = session["did"]

                # Upload blob if file exists
                embed = None
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        file_bytes = f.read()
                    blob_resp = await client.post(
                        "https://bsky.social/xrpc/com.atproto.repo.uploadBlob",
                        content=file_bytes,
                        headers={
                            "Authorization": f"Bearer {access_jwt}",
                            "Content-Type": "image/jpeg",
                        },
                    )
                    if blob_resp.status_code == 200:
                        blob = blob_resp.json().get("blob")
                        embed = {
                            "$type": "app.bsky.embed.images",
                            "images": [{"alt": title[:1000], "image": blob}],
                        }

                # Create post
                now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                record = {
                    "$type": "app.bsky.feed.post",
                    "text": text,
                    "createdAt": now,
                }
                if embed:
                    record["embed"] = embed

                post_resp = await client.post(
                    "https://bsky.social/xrpc/com.atproto.repo.createRecord",
                    headers={
                        "Authorization": f"Bearer {access_jwt}",
                        "Content-Type": "application/json",
                    },
                    content=json.dumps({
                        "repo": did,
                        "collection": "app.bsky.feed.post",
                        "record": record,
                    }),
                )

                if post_resp.status_code == 200:
                    data = post_resp.json()
                    uri = data.get("uri", "")
                    return DeliveryResult(
                        True,
                        platform_content_id=uri,
                        message=f"Posted to Bluesky: {uri}",
                        response_data=data,
                    )
                return DeliveryResult(False, message=f"Bluesky post failed: {post_resp.status_code}")

        except Exception as e:
            logger.error(f"Bluesky delivery error: {e}")
            return DeliveryResult(False, message=f"Bluesky error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# DISCORD ADAPTER (Webhook)
# ─────────────────────────────────────────────
class DiscordAdapter(BasePlatformAdapter):
    platform_id = "discord"
    platform_name = "Discord"
    required_credentials = ["webhook_url"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing Discord webhook_url")

        webhook_url = credentials["webhook_url"]
        title = content.get("title", "New Content")
        description = content.get("description", "")
        artist = content.get("metadata", {}).get("basic", {}).get("artist", "")
        content_type = content.get("content_type", "")
        public_url = self.get_public_file_url(content)

        embed = {
            "title": title,
            "description": description[:2048],
            "color": 0x7C3AED,
            "fields": [],
            "footer": {"text": "Big Mann Entertainment Distribution Hub"},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if artist:
            embed["fields"].append({"name": "Artist", "value": artist, "inline": True})
        if content_type:
            embed["fields"].append({"name": "Type", "value": content_type.capitalize(), "inline": True})
        if public_url:
            embed["url"] = public_url
            embed["fields"].append({"name": "Content Link", "value": f"[View/Download]({public_url})", "inline": False})

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                payload = {"embeds": [embed]}

                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        resp = await client.post(
                            webhook_url,
                            data={"payload_json": json.dumps(payload)},
                            files={"file": (os.path.basename(file_path), f)},
                        )
                else:
                    resp = await client.post(
                        webhook_url,
                        content=json.dumps(payload),
                        headers={"Content-Type": "application/json"},
                    )

                if resp.status_code in (200, 204):
                    return DeliveryResult(True, message="Delivered to Discord channel", response_data={"status": "sent"})
                return DeliveryResult(False, message=f"Discord delivery failed: {resp.status_code} {resp.text[:200]}")

        except Exception as e:
            logger.error(f"Discord delivery error: {e}")
            return DeliveryResult(False, message=f"Discord error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# TELEGRAM ADAPTER (Bot API)
# ─────────────────────────────────────────────
class TelegramAdapter(BasePlatformAdapter):
    platform_id = "telegram"
    platform_name = "Telegram"
    required_credentials = ["bot_token", "chat_id"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing Telegram bot_token or chat_id")

        bot_token = credentials["bot_token"]
        chat_id = credentials["chat_id"]
        title = content.get("title", "New Content")
        description = content.get("description", "")
        content_type = content.get("content_type", "")
        public_url = self.get_public_file_url(content)
        caption = f"*{title}*\n\n{description}"
        if public_url:
            caption += f"\n\n[Content Link]({public_url})"
        caption = caption[:1024]

        base_url = f"https://api.telegram.org/bot{bot_token}"

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        if content_type == "audio":
                            resp = await client.post(
                                f"{base_url}/sendAudio",
                                data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
                                files={"audio": (os.path.basename(file_path), f)},
                            )
                        elif content_type == "video":
                            resp = await client.post(
                                f"{base_url}/sendVideo",
                                data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
                                files={"video": (os.path.basename(file_path), f)},
                            )
                        elif content_type == "image":
                            resp = await client.post(
                                f"{base_url}/sendPhoto",
                                data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
                                files={"photo": (os.path.basename(file_path), f)},
                            )
                        else:
                            resp = await client.post(
                                f"{base_url}/sendDocument",
                                data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"},
                                files={"document": (os.path.basename(file_path), f)},
                            )
                else:
                    resp = await client.post(
                        f"{base_url}/sendMessage",
                        data={"chat_id": chat_id, "text": caption, "parse_mode": "Markdown"},
                    )

                if resp.status_code == 200 and resp.json().get("ok"):
                    msg = resp.json().get("result", {})
                    msg_id = str(msg.get("message_id", ""))
                    return DeliveryResult(
                        True,
                        platform_content_id=msg_id,
                        message=f"Delivered to Telegram: message {msg_id}",
                        response_data={"message_id": msg_id, "chat_id": chat_id},
                    )
                return DeliveryResult(False, message=f"Telegram delivery failed: {resp.status_code} {resp.text[:200]}")

        except Exception as e:
            logger.error(f"Telegram delivery error: {e}")
            return DeliveryResult(False, message=f"Telegram error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# INSTAGRAM ADAPTER (Graph API)
# ─────────────────────────────────────────────
class InstagramAdapter(BasePlatformAdapter):
    platform_id = "instagram"
    platform_name = "Instagram"
    required_credentials = ["access_token", "page_id"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing Instagram access_token or page_id")

        access_token = credentials["access_token"]
        page_id = credentials["page_id"]
        caption = f"{content.get('title', '')} {content.get('description', '')}"[:2200]
        content_type = content.get("content_type", "image")

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                # Use the app's own public URL for media
                file_url = self.get_public_file_url(content)

                if not file_url:
                    return DeliveryResult(False, message="Instagram requires a public media URL")

                # Step 1: Create media container
                container_data = {"caption": caption, "access_token": access_token}
                if content_type == "video":
                    container_data["media_type"] = "VIDEO"
                    container_data["video_url"] = file_url
                else:
                    container_data["image_url"] = file_url

                container_resp = await client.post(
                    f"https://graph.facebook.com/v19.0/{page_id}/media",
                    data=container_data,
                )

                if container_resp.status_code != 200:
                    return DeliveryResult(False, message=f"Instagram container failed: {container_resp.status_code} {container_resp.text[:200]}")

                creation_id = container_resp.json().get("id")

                # Step 2: Publish
                pub_resp = await client.post(
                    f"https://graph.facebook.com/v19.0/{page_id}/media_publish",
                    data={"creation_id": creation_id, "access_token": access_token},
                )

                if pub_resp.status_code == 200:
                    media_id = pub_resp.json().get("id", "")
                    return DeliveryResult(
                        True,
                        platform_content_id=media_id,
                        message=f"Published to Instagram: {media_id}",
                        response_data={"media_id": media_id, "source_url": file_url},
                    )
                return DeliveryResult(False, message=f"Instagram publish failed: {pub_resp.status_code}")

        except Exception as e:
            logger.error(f"Instagram delivery error: {e}")
            return DeliveryResult(False, message=f"Instagram error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# FACEBOOK ADAPTER (Graph API)
# ─────────────────────────────────────────────
class FacebookAdapter(BasePlatformAdapter):
    platform_id = "facebook"
    platform_name = "Facebook"
    required_credentials = ["access_token", "page_id"]

    async def deliver(self, content: dict, credentials: dict, file_path: str = None) -> DeliveryResult:
        if not self.validate_credentials(credentials):
            return DeliveryResult(False, message="Missing Facebook access_token or page_id")

        access_token = credentials["access_token"]
        page_id = credentials["page_id"]
        public_url = self.get_public_file_url(content)
        message_text = f"{content.get('title', '')}\n\n{content.get('description', '')}"
        if public_url:
            message_text += f"\n\n{public_url}"

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                if file_path and os.path.exists(file_path):
                    content_type = content.get("content_type", "")
                    with open(file_path, "rb") as f:
                        if content_type == "video":
                            resp = await client.post(
                                f"https://graph-video.facebook.com/v19.0/{page_id}/videos",
                                data={"description": message_text, "access_token": access_token},
                                files={"source": (os.path.basename(file_path), f)},
                            )
                        else:
                            resp = await client.post(
                                f"https://graph.facebook.com/v19.0/{page_id}/photos",
                                data={"message": message_text, "access_token": access_token},
                                files={"source": (os.path.basename(file_path), f)},
                            )
                elif public_url:
                    # Use the app's public URL to let Facebook fetch the content
                    resp = await client.post(
                        f"https://graph.facebook.com/v19.0/{page_id}/feed",
                        data={"message": message_text, "link": public_url, "access_token": access_token},
                    )
                else:
                    resp = await client.post(
                        f"https://graph.facebook.com/v19.0/{page_id}/feed",
                        data={"message": message_text, "access_token": access_token},
                    )

                if resp.status_code == 200:
                    data = resp.json()
                    post_id = data.get("id", data.get("post_id", ""))
                    return DeliveryResult(
                        True,
                        platform_content_id=post_id,
                        message=f"Published to Facebook: {post_id}",
                        response_data={**data, "source_url": public_url},
                    )
                return DeliveryResult(False, message=f"Facebook post failed: {resp.status_code} {resp.text[:200]}")

        except Exception as e:
            logger.error(f"Facebook delivery error: {e}")
            return DeliveryResult(False, message=f"Facebook error: {str(e)[:200]}")


# ─────────────────────────────────────────────
# ADAPTER REGISTRY
# ─────────────────────────────────────────────
PLATFORM_ADAPTERS: Dict[str, BasePlatformAdapter] = {
    "youtube": YouTubeAdapter(),
    "twitter_x": TwitterAdapter(),
    "tiktok": TikTokAdapter(),
    "soundcloud": SoundCloudAdapter(),
    "vimeo": VimeoAdapter(),
    "bluesky": BlueskyAdapter(),
    "discord": DiscordAdapter(),
    "telegram": TelegramAdapter(),
    "instagram": InstagramAdapter(),
    "facebook": FacebookAdapter(),
}


def get_adapter(platform_id: str) -> Optional[BasePlatformAdapter]:
    """Get the adapter for a platform, or None if not supported."""
    return PLATFORM_ADAPTERS.get(platform_id)


def get_supported_platform_ids() -> list:
    """Return list of platform IDs that have real delivery adapters."""
    return list(PLATFORM_ADAPTERS.keys())
