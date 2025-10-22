# Analytics Configuration Guide

## Overview
The BME Social Connect application now blocks Emergent platform tracking scripts and allows you to configure your own analytics services.

## What Was Changed

### 1. Blocked External Tracking Scripts
The following external tracking services are now blocked:
- ✅ Emergent Platform Analytics (api.emergent.sh, app.emergent.sh)
- ✅ Facebook Pixel (connect.facebook.net)
- ✅ Google Tag Manager (googletagmanager.com)
- ✅ Google Analytics (google-analytics.com)
- ✅ Blitzllama (blitzllama.com)
- ✅ Other third-party tracking services

### 2. Script Blocking Implementation
Location: `/app/frontend/public/index.html`

The blocking script intercepts all dynamically loaded scripts and iframes, preventing external tracking services from loading. You'll see console messages like:
```
[BME] Blocked external tracking script: https://api.emergent.sh/...
[BME] Facebook Pixel call blocked
[BME] Google Analytics call blocked
```

## Configure Your Own Analytics

### PostHog Analytics (Current Default)
PostHog is currently configured and can be customized via environment variables.

**To use your own PostHog credentials:**

1. Edit `/app/frontend/.env.development`:
```bash
REACT_APP_POSTHOG_KEY=your_posthog_key_here
REACT_APP_POSTHOG_HOST=https://us.i.posthog.com
```

2. The application will automatically use your credentials when built/deployed.

### Add Google Analytics (Optional)

1. Add to `/app/frontend/.env.development`:
```bash
REACT_APP_GA_TRACKING_ID=G-XXXXXXXXXX
```

2. Add to `/app/frontend/public/index.html` (before `</head>`):
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=%REACT_APP_GA_TRACKING_ID%"></script>
<script>
  if ('%REACT_APP_GA_TRACKING_ID%' && '%REACT_APP_GA_TRACKING_ID%' !== '') {
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '%REACT_APP_GA_TRACKING_ID%');
  }
</script>
```

### Add Facebook Pixel (Optional)

1. Add to `/app/frontend/.env.development`:
```bash
REACT_APP_FB_PIXEL_ID=XXXXXXXXXXXXXXX
```

2. Add to `/app/frontend/public/index.html` (before `</head>`):
```html
<script>
  if ('%REACT_APP_FB_PIXEL_ID%' && '%REACT_APP_FB_PIXEL_ID%' !== '') {
    !function(f,b,e,v,n,t,s)
    {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
    n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', '%REACT_APP_FB_PIXEL_ID%');
    fbq('track', 'PageView');
  }
</script>
```

### Add Other Analytics Services

Follow the same pattern:
1. Add API key/ID to `.env.development` with `REACT_APP_` prefix
2. Add the service's tracking script to `index.html`
3. Use environment variable placeholders like `%REACT_APP_YOUR_KEY%`

## Apply Changes

After modifying environment variables:

```bash
# Restart frontend to apply changes
sudo supervisorctl restart bme_services:frontend
```

After modifying `index.html`:
```bash
# Frontend has hot reload, but you may need to rebuild
cd /app/frontend
yarn build
sudo supervisorctl restart bme_services:frontend
```

## Verification

1. Open browser DevTools Console
2. Navigate to your application
3. Look for these messages:
   - `[BME] Blocked external tracking script: ...` - Confirms blocking is working
   - No errors from `api.emergent.sh` or `app.emergent.sh` - Confirms Emergent tracking is blocked
   - Your analytics service loading messages - Confirms your analytics are working

## Important Notes

1. **Environment Variables**: The `%REACT_APP_*%` placeholders are replaced during build time by Create React App
2. **Analytics Toggle**: Set `REACT_APP_ENABLE_ANALYTICS=true` to enable PostHog, or `false` to disable all analytics
3. **Production**: Make sure to configure production environment variables in your deployment settings
4. **Privacy**: Ensure compliance with GDPR, CCPA, and other privacy regulations when adding analytics

## Current Configuration

- **Emergent Platform Tracking**: ❌ Blocked
- **Facebook Pixel**: ❌ Blocked
- **Google Analytics**: ❌ Blocked
- **PostHog Analytics**: ✅ Enabled (configurable)
- **Custom Analytics**: ✅ Ready to configure

## Support

If you need help configuring specific analytics services, refer to their official documentation:
- [PostHog Docs](https://posthog.com/docs)
- [Google Analytics Docs](https://developers.google.com/analytics)
- [Facebook Pixel Docs](https://developers.facebook.com/docs/meta-pixel)
