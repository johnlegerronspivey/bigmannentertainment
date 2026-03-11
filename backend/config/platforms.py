"""
Distribution platform configurations.
Extracted from server.py - 119 platforms across social media, streaming, radio, TV, etc.
"""

DISTRIBUTION_PLATFORMS = {
    # Major Social Media Platforms (12 platforms)
    "instagram": {
        "type": "social_media",
        "name": "Instagram",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "supported_formats": ["image", "video"],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "credentials_required": ["access_token"],
        "description": "Photo and video sharing social media platform"
    },
    "twitter": {
        "type": "social_media", 
        "name": "Twitter/X",
        "api_endpoint": "https://api.twitter.com/2",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 50 * 1024 * 1024,  # 50MB
        "credentials_required": ["api_key", "api_secret", "access_token", "access_token_secret"],
        "description": "Microblogging and social networking platform"
    },
    "facebook": {
        "type": "social_media",
        "name": "Facebook",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 200 * 1024 * 1024,  # 200MB
        "credentials_required": ["access_token"],
        "description": "Social networking platform"
    },
    "tiktok": {
        "type": "social_media",
        "name": "TikTok",
        "api_endpoint": "https://open-api.tiktok.com",
        "supported_formats": ["video"],
        "max_file_size": 300 * 1024 * 1024,  # 300MB
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Short-form video sharing platform"
    },
    "youtube": {
        "type": "social_media",
        "name": "YouTube",
        "api_endpoint": "https://www.googleapis.com/youtube/v3",
        "supported_formats": ["video", "audio"],
        "max_file_size": 2 * 1024 * 1024 * 1024,  # 2GB
        "credentials_required": ["api_key", "client_id", "client_secret"],
        "description": "Video sharing and streaming platform"
    },
    "snapchat": {
        "type": "social_media",
        "name": "Snapchat",
        "api_endpoint": "https://adsapi.snapchat.com/v1",
        "supported_formats": ["video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Multimedia messaging and content sharing"
    },
    "linkedin": {
        "type": "social_media",
        "name": "LinkedIn",
        "api_endpoint": "https://api.linkedin.com/v2",
        "supported_formats": ["video", "image", "audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Professional networking platform"
    },
    "pinterest": {
        "type": "social_media",
        "name": "Pinterest",
        "api_endpoint": "https://api.pinterest.com/v5",
        "supported_formats": ["image", "video"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["access_token"],
        "description": "Visual discovery and idea platform"
    },
    "reddit": {
        "type": "social_media",
        "name": "Reddit",
        "api_endpoint": "https://oauth.reddit.com/api",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Social news aggregation and discussion"
    },
    "discord": {
        "type": "social_media",
        "name": "Discord",
        "api_endpoint": "https://discord.com/api/v10",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["bot_token"],
        "description": "Communication platform for communities"
    },
    "telegram": {
        "type": "social_media",
        "name": "Telegram",
        "api_endpoint": "https://api.telegram.org/bot",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["bot_token"],
        "description": "Cloud-based instant messaging"
    },
    "whatsapp_business": {
        "type": "social_media",
        "name": "WhatsApp Business",
        "api_endpoint": "https://graph.facebook.com/v18.0",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["access_token", "phone_number_id"],
        "description": "Business messaging platform"
    },
    "threads": {
        "type": "social_media",
        "name": "Threads",
        "api_endpoint": "https://graph.threads.net/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["access_token"],
        "description": "Meta's text-based conversation platform"
    },
    "tumblr": {
        "type": "social_media",
        "name": "Tumblr",
        "api_endpoint": "https://api.tumblr.com/v2",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key", "api_secret", "access_token"],
        "description": "Microblogging platform for creative expression"
    },
    "theshaderoom": {
        "type": "social_media",
        "name": "The Shade Room",
        "api_endpoint": "https://api.theshaderoom.com/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Entertainment and celebrity news platform"
    },
    "hollywoodunlocked": {
        "type": "social_media",
        "name": "Hollywood Unlocked",
        "api_endpoint": "https://api.hollywoodunlocked.com/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 150 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Celebrity news and entertainment platform"
    },
    "snapchat_enhanced": {
        "type": "social_media",
        "name": "Snapchat Enhanced",
        "api_endpoint": "https://adsapi.snapchat.com/v1",
        "supported_formats": ["video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret", "access_token"],
        "description": "Enhanced multimedia messaging and content sharing"
    },
    "onlyfans": {
        "type": "social_media",
        "name": "OnlyFans",
        "api_endpoint": "https://onlyfans.com/api2/v2",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["user_id", "auth_token", "user_agent"],
        "description": "Content subscription and monetization platform for creators"
    },
    "fansly": {
        "type": "social_media",
        "name": "Fansly",
        "api_endpoint": "https://apiv3.fansly.com/api/v1",
        "supported_formats": ["image", "video", "audio"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["auth_token", "user_agent"],
        "description": "Creator subscription platform for exclusive content and fan engagement"
    },

    # Major Music Streaming Platforms (16 platforms)
    "spotify": {
        "type": "music_streaming",
        "name": "Spotify",
        "api_endpoint": "https://api.spotify.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "Music streaming and playlist curation"
    },
    "apple_music": {
        "type": "music_streaming",
        "name": "Apple Music",
        "api_endpoint": "https://api.music.apple.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["developer_token", "music_user_token"],
        "description": "Apple's music streaming service"
    },
    "amazon_music": {
        "type": "music_streaming",
        "name": "Amazon Music",
        "api_endpoint": "https://api.amazonalexa.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "Amazon's music streaming platform"
    },
    "tidal": {
        "type": "music_streaming",
        "name": "Tidal",
        "api_endpoint": "https://api.tidal.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "High-fidelity music streaming"
    },
    "deezer": {
        "type": "music_streaming",
        "name": "Deezer",
        "api_endpoint": "https://api.deezer.com",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["app_id", "secret_key"],
        "description": "Music streaming and discovery"
    },
    "pandora": {
        "type": "music_streaming",
        "name": "Pandora",
        "api_endpoint": "https://api.pandora.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["partner_id", "partner_key"],
        "description": "Personalized radio streaming"
    },
    "soundcloud": {
        "type": "music_streaming",
        "name": "SoundCloud",
        "api_endpoint": "https://api.soundcloud.com",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "Audio sharing platform"
    },
    "bandcamp": {
        "type": "music_streaming",
        "name": "Bandcamp",
        "api_endpoint": "https://bandcamp.com/api",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Artist-to-fan music platform"
    },
    "youtube_music": {
        "type": "music_streaming",
        "name": "YouTube Music",
        "api_endpoint": "https://www.googleapis.com/youtube/v3",
        "supported_formats": ["audio", "video"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key", "client_id"],
        "description": "YouTube's music streaming service"
    },
    "audiomack": {
        "type": "music_streaming",
        "name": "Audiomack",
        "api_endpoint": "https://api.audiomack.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Hip-hop and R&B streaming platform"
    },
    "mixcloud": {
        "type": "music_streaming",
        "name": "Mixcloud",
        "api_endpoint": "https://api.mixcloud.com",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "DJ mixes and radio shows platform"
    },
    "reverbnation": {
        "type": "music_streaming",
        "name": "ReverbNation",
        "api_endpoint": "https://api.reverbnation.com/v2",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Music promotion and distribution"
    },
    "datpiff": {
        "type": "music_streaming",
        "name": "DatPiff",
        "api_endpoint": "https://www.datpiff.com/api",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Mixtape hosting platform"
    },
    "spinrilla": {
        "type": "music_streaming",
        "name": "Spinrilla",
        "api_endpoint": "https://spinrilla.com/api",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Hip-hop mixtape platform"
    },
    "napster": {
        "type": "music_streaming",
        "name": "Napster",
        "api_endpoint": "https://api.napster.com/v2.2",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key", "api_secret"],
        "description": "Music streaming service"
    },
    "livemixtapes": {
        "type": "music_streaming",
        "name": "LiveMixtapes.com",
        "api_endpoint": "https://api.livemixtapes.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 150 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Hip-hop mixtape hosting and streaming platform"
    },
    "mymixtapez": {
        "type": "music_streaming",
        "name": "MyMixtapez.com",
        "api_endpoint": "https://api.mymixtapez.com/v2",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Premier mixtape platform for independent artists"
    },
    "worldstarhiphop": {
        "type": "music_streaming",
        "name": "WorldStar Hip Hop",
        "api_endpoint": "https://api.worldstarhiphop.com/v1",
        "supported_formats": ["audio", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Leading hip-hop content and music platform"
    },
    "revolt": {
        "type": "music_streaming",
        "name": "Revolt",
        "api_endpoint": "https://api.revolt.tv/v1",
        "supported_formats": ["audio", "video"],
        "max_file_size": 300 * 1024 * 1024,
        "credentials_required": ["api_key", "client_secret"],
        "description": "Music and culture streaming platform focused on hip-hop and R&B"
    },

    # Podcast Platforms (8 platforms)
    "apple_podcasts": {
        "type": "podcast",
        "name": "Apple Podcasts",
        "api_endpoint": "https://itunespartner.apple.com/api",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["apple_id", "password"],
        "description": "Apple's podcast platform"
    },
    "spotify_podcasts": {
        "type": "podcast",
        "name": "Spotify Podcasts",
        "api_endpoint": "https://api.spotify.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "Spotify's podcast platform"
    },
    "google_podcasts": {
        "type": "podcast",
        "name": "Google Podcasts",
        "api_endpoint": "https://podcasts.google.com/api",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Google's podcast platform"
    },
    "stitcher": {
        "type": "podcast",
        "name": "Stitcher",
        "api_endpoint": "https://api.stitcher.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Podcast streaming platform"
    },
    "overcast": {
        "type": "podcast",
        "name": "Overcast",
        "api_endpoint": "https://overcast.fm/api",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "iOS podcast app"
    },
    "pocketcasts": {
        "type": "podcast",
        "name": "Pocket Casts",
        "api_endpoint": "https://api.pocketcasts.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Cross-platform podcast app"
    },
    "castbox": {
        "type": "podcast",
        "name": "Castbox",
        "api_endpoint": "https://castbox.fm/api",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Global podcast platform"
    },
    "anchor": {
        "type": "podcast",
        "name": "Anchor",
        "api_endpoint": "https://anchor.fm/api",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Podcast creation and hosting"
    },

    # Radio & Broadcasting (10 platforms)
    "iheartradio": {
        "type": "radio",
        "name": "iHeartRadio",
        "api_endpoint": "https://api.iheart.com/v3",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Digital radio platform"
    },
    "siriusxm": {
        "type": "radio",
        "name": "SiriusXM",
        "api_endpoint": "https://api.siriusxm.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Satellite radio service"
    },
    "tunein": {
        "type": "radio",
        "name": "TuneIn",
        "api_endpoint": "https://api.tunein.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Internet radio platform"
    },
    "radio_com": {
        "type": "radio",
        "name": "Radio.com",
        "api_endpoint": "https://api.radio.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Live radio streaming"
    },
    "live365": {
        "type": "radio",
        "name": "Live365",
        "api_endpoint": "https://api.live365.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Internet radio broadcasting"
    },
    "radioio": {
        "type": "radio",
        "name": "RadioIO",
        "api_endpoint": "https://radioio.com/api",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Online radio network"
    },
    "streema": {
        "type": "radio",
        "name": "Streema",
        "api_endpoint": "https://streema.com/api",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Radio station discovery"
    },
    "radionet": {
        "type": "radio",
        "name": "radio.net",
        "api_endpoint": "https://api.radio.net/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Global radio platform"
    },
    "zeno_fm": {
        "type": "radio",
        "name": "Zeno.FM",
        "api_endpoint": "https://zeno.fm/api",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Free internet radio hosting"
    },
    "shoutcast": {
        "type": "radio",
        "name": "SHOUTcast",
        "api_endpoint": "https://api.shoutcast.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Internet radio streaming"
    },

    # Television & Video Streaming (9 platforms)
    "netflix": {
        "type": "video_streaming",
        "name": "Netflix",
        "api_endpoint": "https://api.netflix.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,  # 5GB
        "credentials_required": ["partner_key", "content_id"],
        "description": "Global video streaming platform"
    },
    "hulu": {
        "type": "video_streaming",
        "name": "Hulu",
        "api_endpoint": "https://api.hulu.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "US video streaming service"
    },
    "amazon_prime_video": {
        "type": "video_streaming",
        "name": "Amazon Prime Video",
        "api_endpoint": "https://api.amazonvideo.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,
        "credentials_required": ["access_key", "secret_key"],
        "description": "Amazon's video streaming service"
    },
    "hbo_max": {
        "type": "video_streaming",
        "name": "HBO Max",
        "api_endpoint": "https://api.hbomax.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Warner Bros. streaming platform"
    },
    "disney_plus": {
        "type": "video_streaming",
        "name": "Disney+",
        "api_endpoint": "https://api.disneyplus.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,
        "credentials_required": ["content_partner_key"],
        "description": "Disney's streaming service"
    },
    "paramount_plus": {
        "type": "video_streaming",
        "name": "Paramount+",
        "api_endpoint": "https://api.paramountplus.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "CBS/Paramount streaming platform"
    },
    "peacock": {
        "type": "video_streaming",
        "name": "Peacock",
        "api_endpoint": "https://api.peacocktv.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,
        "credentials_required": ["content_key"],
        "description": "NBCUniversal streaming service"
    },
    "roku_channel": {
        "type": "video_streaming",
        "name": "The Roku Channel",
        "api_endpoint": "https://api.roku.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["developer_id", "api_key"],
        "description": "Roku's free streaming platform"
    },
    "espn": {
        "type": "video_streaming",
        "name": "ESPN",
        "api_endpoint": "https://api.espn.com/v1",
        "supported_formats": ["video", "audio"],
        "max_file_size": 5 * 1024 * 1024 * 1024,  # 5GB
        "credentials_required": ["content_partner_key", "api_key"],
        "description": "Sports streaming and broadcasting platform"
    },

    # Music Industry Rights Organizations (5 platforms)
    "ascap": {
        "type": "rights_organization",
        "name": "ASCAP",
        "api_endpoint": "https://api.ascap.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["member_id", "api_key"],
        "description": "American Society of Composers, Authors and Publishers"
    },
    "bmi": {
        "type": "rights_organization",
        "name": "BMI",
        "api_endpoint": "https://api.bmi.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["writer_id", "publisher_id", "api_key"],
        "description": "Broadcast Music, Inc. - Performance rights organization"
    },
    "sesac": {
        "type": "rights_organization",
        "name": "SESAC",
        "api_endpoint": "https://api.sesac.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["writer_id", "publisher_id", "api_key"],
        "description": "Society of European Stage Authors and Composers"
    },
    "soundexchange": {
        "type": "rights_organization",
        "name": "SoundExchange",
        "api_endpoint": "https://api.soundexchange.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["account_id", "api_key"],
        "description": "Digital performance rights organization"
    },
    "harry_fox_agency": {
        "type": "rights_organization",
        "name": "Harry Fox Agency",
        "api_endpoint": "https://api.harryfox.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["publisher_id", "api_key"],
        "description": "Mechanical licensing agency"
    },

    # Web3 and Blockchain Platforms (10 platforms)
    "ethereum_mainnet": {
        "type": "blockchain",
        "name": "Ethereum Mainnet",
        "api_endpoint": "https://mainnet.infura.io/v3",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["infura_project_id", "private_key"],
        "description": "Ethereum blockchain for NFT minting"
    },
    "polygon_matic": {
        "type": "blockchain",
        "name": "Polygon (MATIC)",
        "api_endpoint": "https://polygon-mainnet.infura.io/v3",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["infura_project_id", "private_key"],
        "description": "Low-cost Polygon network for NFTs"
    },
    "solana_mainnet": {
        "type": "blockchain",
        "name": "Solana Mainnet",
        "api_endpoint": "https://api.mainnet-beta.solana.com",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["private_key"],
        "description": "High-speed blockchain for NFTs"
    },
    "avalanche": {
        "type": "blockchain",
        "name": "Avalanche",
        "api_endpoint": "https://api.avax.network",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["private_key"],
        "description": "Avalanche blockchain network"
    },
    "binance_smart_chain": {
        "type": "blockchain",
        "name": "Binance Smart Chain",
        "api_endpoint": "https://bsc-dataseed1.binance.org",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["private_key"],
        "description": "Binance's blockchain network"
    },
    "audius": {
        "type": "web3_music",
        "name": "Audius",
        "api_endpoint": "https://api.audius.co/v1",
        "supported_formats": ["audio"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["audius_private_key", "user_id"],
        "description": "Decentralized music streaming platform"
    },
    "catalog": {
        "type": "web3_music",
        "name": "Catalog",
        "api_endpoint": "https://api.catalog.works/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["catalog_api_key", "wallet_private_key"],
        "description": "NFT music marketplace"
    },
    "sound_xyz": {
        "type": "web3_music",
        "name": "Sound.xyz",
        "api_endpoint": "https://api.sound.xyz/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["sound_api_key", "wallet_private_key"],
        "description": "Web3 music platform with fan funding"
    },
    "royal": {
        "type": "web3_music",
        "name": "Royal",
        "api_endpoint": "https://api.royal.io/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["royal_api_key", "artist_id"],
        "description": "Music NFT ownership and royalty sharing"
    },
    "opensea": {
        "type": "nft_marketplace",
        "name": "OpenSea",
        "api_endpoint": "https://api.opensea.io/api/v1",
        "supported_formats": ["audio", "video", "image"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Leading NFT marketplace"
    },

    # International Music Platforms (8 platforms)
    "joox": {
        "type": "music_streaming",
        "name": "JOOX",
        "api_endpoint": "https://api.joox.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Asian music streaming platform"
    },
    "anghami": {
        "type": "music_streaming",
        "name": "Anghami",
        "api_endpoint": "https://api.anghami.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Middle Eastern music platform"
    },
    "gaana": {
        "type": "music_streaming",
        "name": "Gaana",
        "api_endpoint": "https://api.gaana.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Indian music streaming service"
    },
    "jiosaavn": {
        "type": "music_streaming",
        "name": "JioSaavn",
        "api_endpoint": "https://api.jiosaavn.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Indian music streaming platform"
    },
    "yandex_music": {
        "type": "music_streaming",
        "name": "Yandex Music",
        "api_endpoint": "https://api.music.yandex.net/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Russian music streaming service"
    },
    "qq_music": {
        "type": "music_streaming",
        "name": "QQ Music",
        "api_endpoint": "https://api.y.qq.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Chinese music streaming platform"
    },
    "netease_cloud_music": {
        "type": "music_streaming",
        "name": "NetEase Cloud Music",
        "api_endpoint": "https://api.music.163.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Chinese music streaming service"
    },
    "boomplay": {
        "type": "music_streaming",
        "name": "Boomplay",
        "api_endpoint": "https://api.boomplay.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "African music streaming platform"
    },

    # Additional Digital Platforms (15 platforms)
    "twitch": {
        "type": "live_streaming",
        "name": "Twitch",
        "api_endpoint": "https://api.twitch.tv/helix",
        "supported_formats": ["video", "audio"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "Live streaming platform for gamers"
    },
    "kick": {
        "type": "live_streaming",
        "name": "Kick",
        "api_endpoint": "https://kick.com/api/v1",
        "supported_formats": ["video", "audio"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Creator-focused live streaming"
    },
    "rumble": {
        "type": "video_platform",
        "name": "Rumble",
        "api_endpoint": "https://rumble.com/api/v1",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Alternative video platform"
    },
    "dailymotion": {
        "type": "video_platform",
        "name": "Dailymotion",
        "api_endpoint": "https://www.dailymotion.com/api",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "European video sharing platform"
    },
    "vimeo": {
        "type": "video_platform",
        "name": "Vimeo",
        "api_endpoint": "https://api.vimeo.com",
        "supported_formats": ["video"],
        "max_file_size": 5 * 1024 * 1024 * 1024,
        "credentials_required": ["access_token"],
        "description": "Professional video platform"
    },
    "odysee": {
        "type": "video_platform",
        "name": "Odysee",
        "api_endpoint": "https://api.odysee.com/v1",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Decentralized video platform"
    },
    "bitchute": {
        "type": "video_platform",
        "name": "BitChute",
        "api_endpoint": "https://www.bitchute.com/api/v1",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Alternative video platform"
    },
    "brighteon": {
        "type": "video_platform",
        "name": "Brighteon",
        "api_endpoint": "https://www.brighteon.com/api/v1",
        "supported_formats": ["video"],
        "max_file_size": 2 * 1024 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Free speech video platform"
    },
    "gettr": {
        "type": "social_media",
        "name": "GETTR",
        "api_endpoint": "https://api.gettr.com/v1",
        "supported_formats": ["video", "image", "audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Social networking platform"
    },
    "gab": {
        "type": "social_media",
        "name": "Gab",
        "api_endpoint": "https://gab.com/api/v1",
        "supported_formats": ["video", "image", "audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Free speech social network"
    },
    "parler": {
        "type": "social_media",
        "name": "Parler",
        "api_endpoint": "https://api.parler.com/v1",
        "supported_formats": ["video", "image", "audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Alternative social media platform"
    },
    "truth_social": {
        "type": "social_media",
        "name": "Truth Social",
        "api_endpoint": "https://truthsocial.com/api/v1",
        "supported_formats": ["video", "image", "audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Social media platform"
    },
    "clubhouse": {
        "type": "audio_social",
        "name": "Clubhouse",
        "api_endpoint": "https://www.clubhouseapi.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["api_key"],
        "description": "Audio-based social networking"
    },
    "spaces": {
        "type": "audio_social",
        "name": "Twitter Spaces",
        "api_endpoint": "https://api.twitter.com/2",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["bearer_token"],
        "description": "Twitter's audio spaces feature"
    },
    "greenroom": {
        "type": "audio_social",
        "name": "Greenroom (Spotify Live)",
        "api_endpoint": "https://api.spotify.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["client_id", "client_secret"],
        "description": "Spotify's live audio platform"
    },

    # Model Agencies & Photography Platforms (15 platforms)
    "img_models": {
        "type": "model_agency",
        "name": "IMG Models",
        "api_endpoint": "https://api.imgmodels.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,  # 500MB for high-res photos
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "Premier international modeling agency"
    },
    "elite_model_management": {
        "type": "model_agency",
        "name": "Elite Model Management",
        "api_endpoint": "https://api.elitemodel.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "Global luxury modeling agency"
    },
    "ford_models": {
        "type": "model_agency",
        "name": "Ford Models",
        "api_endpoint": "https://api.fordmodels.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "Historic American modeling agency"
    },
    "wilhelmina_models": {
        "type": "model_agency",
        "name": "Wilhelmina Models",
        "api_endpoint": "https://api.wilhelmina.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "International modeling and talent agency"
    },
    "next_management": {
        "type": "model_agency",
        "name": "Next Management",
        "api_endpoint": "https://api.nextmanagement.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "Global fashion model management"
    },
    "women_management": {
        "type": "model_agency",
        "name": "Women Management",
        "api_endpoint": "https://api.womenmanagement.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "Premier women's modeling agency"
    },
    "society_management": {
        "type": "model_agency",
        "name": "The Society Management",
        "api_endpoint": "https://api.thesocietynyc.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "High-fashion modeling agency"
    },
    "storm_models": {
        "type": "model_agency",
        "name": "Storm Models",
        "api_endpoint": "https://api.stormmodels.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "British modeling agency"
    },
    "premier_model_management": {
        "type": "model_agency",
        "name": "Premier Model Management",
        "api_endpoint": "https://api.premiermodelmanagement.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "Leading UK modeling agency"
    },
    "select_model_management": {
        "type": "model_agency",
        "name": "Select Model Management",
        "api_endpoint": "https://api.selectmodel.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "International fashion model agency"
    },
    "models_com": {
        "type": "model_platform",
        "name": "Models.com",
        "api_endpoint": "https://api.models.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 200 * 1024 * 1024,
        "credentials_required": ["api_key", "photographer_profile"],
        "description": "Global fashion industry platform"
    },
    "la_models": {
        "type": "model_agency",
        "name": "LA Models",
        "api_endpoint": "https://api.lamodels.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "Los Angeles modeling agency"
    },
    "new_york_models": {
        "type": "model_agency",
        "name": "New York Models",
        "api_endpoint": "https://api.newyorkmodels.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "New York based modeling agency"
    },
    "dna_models": {
        "type": "model_agency",
        "name": "DNA Models",
        "api_endpoint": "https://api.dnamodels.com/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "Fashion and commercial modeling agency"
    },
    "modelwerk": {
        "type": "model_agency",
        "name": "Modelwerk",
        "api_endpoint": "https://api.modelwerk.de/v1",
        "supported_formats": ["image", "video"],
        "max_file_size": 500 * 1024 * 1024,
        "credentials_required": ["agency_id", "api_key", "photographer_license"],
        "description": "German fashion modeling agency"
    },

    # Music Data Exchange & Licensing Platforms (2 platforms)
    "mlc": {
        "type": "music_licensing",
        "name": "Mechanical Licensing Collective (MLC)",
        "api_endpoint": "https://api.themlc.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["mlc_account_id", "api_key"],
        "description": "Mechanical licensing and royalty collection for digital music"
    },
    "mde": {
        "type": "music_data_exchange",
        "name": "Music Data Exchange (MDE)",
        "api_endpoint": "https://api.musicdataexchange.com/v1",
        "supported_formats": ["audio"],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["mde_publisher_id", "api_key"],
        "description": "Comprehensive music metadata management and rights information exchange"
    },
    "github": {
        "type": "social_media",
        "name": "GitHub",
        "api_endpoint": "https://api.github.com",
        "supported_formats": [],
        "max_file_size": 100 * 1024 * 1024,
        "credentials_required": ["access_token"],
        "description": "Developer platform for code hosting and collaboration"
    },
    "medium": {
        "type": "social_media",
        "name": "Medium",
        "api_endpoint": "https://api.medium.com/v1",
        "supported_formats": [],
        "max_file_size": 25 * 1024 * 1024,
        "credentials_required": ["access_token"],
        "description": "Online publishing platform for writers and readers"
    },
    "bluesky": {
        "type": "social_media",
        "name": "Bluesky",
        "api_endpoint": "https://bsky.social/xrpc",
        "supported_formats": ["image", "video"],
        "max_file_size": 50 * 1024 * 1024,
        "credentials_required": ["handle", "app_password"],
        "description": "Decentralized social networking platform"
    },
}

