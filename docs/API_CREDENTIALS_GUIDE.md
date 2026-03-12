# API Credentials Guide — Live Platform Adapters

This guide covers the **10 platforms** with live API delivery adapters in the Distribution Hub. For each platform, you'll find the required credentials, where to obtain them, and step-by-step setup instructions.

---

## Table of Contents

| # | Platform | Credentials Needed | Developer Portal |
|---|----------|--------------------|-----------------|
| 1 | [YouTube](#1-youtube) | `access_token` | [Google Cloud Console](https://console.cloud.google.com/) |
| 2 | [Twitter/X](#2-twitterx) | `bearer_token` | [Twitter Developer Portal](https://developer.twitter.com/) |
| 3 | [TikTok](#3-tiktok) | `access_token` | [TikTok for Developers](https://developers.tiktok.com/) |
| 4 | [SoundCloud](#4-soundcloud) | `access_token` | [SoundCloud Developer](https://soundcloud.com/you/apps) |
| 5 | [Vimeo](#5-vimeo) | `access_token` | [Vimeo Developer](https://developer.vimeo.com/) |
| 6 | [Bluesky](#6-bluesky) | `handle`, `app_password` | [Bluesky App Passwords](https://bsky.app/settings/app-passwords) |
| 7 | [Discord](#7-discord) | `webhook_url` | Discord Server Settings |
| 8 | [Telegram](#8-telegram) | `bot_token`, `chat_id` | [@BotFather on Telegram](https://t.me/BotFather) |
| 9 | [Instagram](#9-instagram) | `access_token`, `page_id` | [Meta for Developers](https://developers.facebook.com/) |
| 10 | [Facebook](#10-facebook) | `access_token`, `page_id` | [Meta for Developers](https://developers.facebook.com/) |

---

## 1. YouTube

**API Used:** YouTube Data API v3 (Resumable Upload)

### Required Credentials
| Field | Description |
|-------|-------------|
| `access_token` | OAuth 2.0 access token with `youtube.upload` scope |

### How to Obtain

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services > Library**
4. Search for and enable **YouTube Data API v3**
5. Go to **APIs & Services > Credentials**
6. Click **Create Credentials > OAuth 2.0 Client ID**
7. Configure the OAuth consent screen (External or Internal)
8. Set application type to **Web application**
9. Add authorized redirect URIs for your app
10. Use the client ID and secret to perform the OAuth 2.0 flow and obtain an `access_token`

### Scopes Required
- `https://www.googleapis.com/auth/youtube.upload`
- `https://www.googleapis.com/auth/youtube` (for full access)

### Notes
- Access tokens expire after 1 hour; use refresh tokens for long-lived access
- Videos are uploaded as **private** by default through our adapter
- Maximum file size: 128 GB (API limit), but practical uploads depend on your connection

---

## 2. Twitter/X

**API Used:** Twitter API v2 + v1.1 (Media Upload)

### Required Credentials
| Field | Description |
|-------|-------------|
| `bearer_token` | App-level Bearer Token for v2 API (also accepts `access_token`) |

### How to Obtain

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Sign up for a developer account (Free tier available)
3. Create a new **Project** and **App**
4. Navigate to your App's **Keys and Tokens** section
5. Generate a **Bearer Token** under "Authentication Tokens"
6. For media uploads, you'll also need OAuth 1.0a User Context tokens

### Access Levels
| Tier | Tweet Cap | Media Upload |
|------|-----------|-------------|
| Free | 1,500/month | No |
| Basic ($100/mo) | 3,000/month | Yes |
| Pro ($5,000/mo) | 300,000/month | Yes |

### Notes
- The Free tier does **not** support media uploads; Basic or higher is recommended
- Tweet text is truncated to 280 characters (title + description + content link)
- Media upload still uses the v1.1 endpoint (`upload.twitter.com`)

---

## 3. TikTok

**API Used:** TikTok Content Posting API v2

### Required Credentials
| Field | Description |
|-------|-------------|
| `access_token` | OAuth access token from TikTok Login Kit |

### How to Obtain

1. Go to [TikTok for Developers](https://developers.tiktok.com/)
2. Create a developer account
3. Register a new application
4. Request access to the **Content Posting API**
5. Configure OAuth redirect URIs
6. Implement the OAuth flow to get a user access token

### Notes
- TikTok **requires a video file** — text-only posts are not supported
- Videos are initially posted as **Self Only** (private) visibility
- The Content Posting API requires app review and approval from TikTok
- Maximum video size varies by account tier

---

## 4. SoundCloud

**API Used:** SoundCloud HTTP API

### Required Credentials
| Field | Description |
|-------|-------------|
| `access_token` | OAuth 2.0 access token |

### How to Obtain

1. Go to [SoundCloud Developer Portal](https://soundcloud.com/you/apps)
2. Register a new application
3. Note your **Client ID** and **Client Secret**
4. Implement the OAuth 2.0 authorization code flow:
   - Redirect user to `https://soundcloud.com/connect?client_id=YOUR_ID&redirect_uri=YOUR_URI&response_type=code`
   - Exchange the authorization code for an access token
5. Use the access token for API calls

### Notes
- SoundCloud **requires an audio file** — no metadata-only uploads
- Tracks are uploaded as **private** by default
- SoundCloud has been limiting new API registrations — apply early
- Supported formats: MP3, WAV, FLAC, AIFF, OGG

---

## 5. Vimeo

**API Used:** Vimeo API v3.4 (TUS Resumable Upload)

### Required Credentials
| Field | Description |
|-------|-------------|
| `access_token` | Personal access token or OAuth token |

### How to Obtain

1. Go to [Vimeo Developer Portal](https://developer.vimeo.com/)
2. Click **My Apps** and create a new app
3. Under **Authentication**, generate a **Personal Access Token** with these scopes:
   - `upload`
   - `create`
   - `edit`
   - `video_files`
4. Copy the token — it won't be shown again

### Account Requirements
| Plan | Upload Limit | API Access |
|------|-------------|------------|
| Basic (Free) | 500 MB/week | Yes |
| Plus | 5 GB/week | Yes |
| Pro | 20 GB/week | Yes |
| Business | No limit | Yes |

### Notes
- Videos are uploaded with **nobody** privacy (hidden) by default
- Uses TUS resumable upload protocol for reliability
- A Vimeo Plus plan or higher is recommended for regular uploads

---

## 6. Bluesky

**API Used:** AT Protocol (Authenticated Transfer Protocol)

### Required Credentials
| Field | Description |
|-------|-------------|
| `handle` | Your Bluesky handle (e.g., `yourname.bsky.social`) |
| `app_password` | An app-specific password (not your main password) |

### How to Obtain

1. Log in to [Bluesky](https://bsky.app/)
2. Go to **Settings** > **Privacy and Security** > **App Passwords**
   - Direct link: [bsky.app/settings/app-passwords](https://bsky.app/settings/app-passwords)
3. Click **Add App Password**
4. Give it a name (e.g., "Distribution Hub")
5. Copy the generated password immediately — it won't be shown again

### Notes
- App passwords are safer than using your main password
- Posts are limited to **300 characters** (title + description + link)
- Image attachments are supported (uploaded as blobs)
- No cost — Bluesky is free to use

---

## 7. Discord

**API Used:** Discord Webhooks

### Required Credentials
| Field | Description |
|-------|-------------|
| `webhook_url` | A Discord webhook URL for the target channel |

### How to Obtain

1. Open your Discord server
2. Go to **Server Settings** > **Integrations** > **Webhooks**
   - Or right-click a channel > **Edit Channel** > **Integrations** > **Webhooks**
3. Click **New Webhook**
4. Give it a name (e.g., "Distribution Hub")
5. Select the target channel
6. Click **Copy Webhook URL**

The URL looks like: `https://discord.com/api/webhooks/XXXXXXX/YYYYYYY`

### Notes
- No developer application needed — webhooks are built into Discord
- Messages appear as rich embeds with title, description, and content links
- File attachments are supported (up to 25 MB for non-Nitro servers)
- Rate limit: 30 messages per 60 seconds per webhook

---

## 8. Telegram

**API Used:** Telegram Bot API

### Required Credentials
| Field | Description |
|-------|-------------|
| `bot_token` | Bot API token from @BotFather |
| `chat_id` | Target chat/group/channel ID |

### How to Obtain

#### Step 1: Create a Bot
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`
3. Choose a display name and username for your bot
4. Copy the **bot token** (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Step 2: Get the Chat ID
1. Add your bot to the target group or channel (as admin)
2. Send a message in the group
3. Open `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in a browser
4. Find the `chat.id` value in the JSON response
   - Group IDs are negative numbers (e.g., `-1001234567890`)
   - Channel IDs start with `-100`

### Notes
- Content is delivered based on type: audio, video, photo, or document
- Captions support Markdown formatting
- File size limit: 50 MB (for bots)
- No cost — Telegram Bot API is free

---

## 9. Instagram

**API Used:** Instagram Graph API (via Meta/Facebook)

### Required Credentials
| Field | Description |
|-------|-------------|
| `access_token` | Page-level access token from Meta |
| `page_id` | Instagram Business Account ID |

### How to Obtain

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app (type: **Business**)
3. Add the **Instagram Graph API** product
4. Connect a **Facebook Page** to an **Instagram Business** or **Creator** account
5. In the Graph API Explorer:
   - Select your app
   - Generate a **User Access Token** with `instagram_basic`, `instagram_content_publish`, `pages_show_list` permissions
   - Exchange for a long-lived token
6. Get your Instagram Business Account ID:
   - Call `GET /{page-id}?fields=instagram_business_account` 
   - Use the returned `instagram_business_account.id` as your `page_id`

### Requirements
- Instagram account must be **Business** or **Creator** type (not Personal)
- Must be linked to a Facebook Page
- Media must be accessible via a **public URL** (our adapter uses the app's content URL)

### Notes
- Images and videos are published via a two-step process (create container → publish)
- The Instagram API does **not** support direct file uploads — media must be hosted at a public URL
- Caption limit: 2,200 characters

---

## 10. Facebook

**API Used:** Facebook Graph API v19.0

### Required Credentials
| Field | Description |
|-------|-------------|
| `access_token` | Page Access Token |
| `page_id` | Facebook Page ID |

### How to Obtain

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app (type: **Business**)
3. Add the **Facebook Pages API** product
4. In the Graph API Explorer:
   - Select your app
   - Generate a **User Access Token** with `pages_manage_posts`, `pages_read_engagement` permissions
   - Call `GET /me/accounts` to list your Pages
   - Copy the Page's `id` and its Page-level `access_token`
5. For a long-lived token:
   - Exchange the short-lived token for a long-lived user token
   - Then get a Page token from the long-lived user token (Page tokens from long-lived user tokens don't expire)

### Notes
- Supports text posts, link shares, photo uploads, and video uploads
- Videos are uploaded to the Page's video library
- The adapter includes the content's public URL as a link in posts
- Rate limits apply based on your app's tier

---

## Security Best Practices

1. **Never share credentials** in plain text via email or chat
2. **Use app-specific passwords** where available (Bluesky)
3. **Generate separate tokens** for each application — don't reuse tokens across services
4. **Store credentials securely** — they are encrypted at rest in our database
5. **Rotate tokens periodically** — especially after team member changes
6. **Use the minimum permissions** required for each platform
7. **Monitor API usage** — set up alerts for unusual activity on each developer portal

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| "Invalid token" error | Token may have expired — regenerate and reconnect |
| "Permission denied" | Check that your token has the required scopes/permissions |
| "Rate limit exceeded" | Wait and retry, or upgrade your API tier |
| "Media URL not accessible" | Ensure your app's `APP_BASE_URL` is publicly accessible |
| Upload fails silently | Check the Delivery Tracking tab for detailed error messages |

---

*Last updated: February 2026*
