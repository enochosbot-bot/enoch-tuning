# TikTok Automation with OpenClaw — Larry Case Study
**Date:** 2026-02-15
**Source:** Oliver Henry (@oliverhenry on X) + Larry (@LarryClawerence)
**Apps:** Snugly (AI room redesign), Liply (lip filler preview)

## Results
- 500K+ TikTok views in 5 days
- 234K views top post
- 4 posts over 100K views
- 108 paying subscribers, $588/month MRR
- Cost per post: ~$0.50 ($0.25 with batch API)

## Stack
- Old gaming PC (NVIDIA 2070 Super) running Ubuntu
- OpenClaw + Claude
- OpenAI gpt-image-1.5 for image generation
- Postiz for TikTok posting API (uploads as drafts)
- Manual step: add trending music + publish (~60 seconds)

## Key Lessons

### Hook Formula (THE insight)
`[Another person] + [conflict/doubt] → showed them AI → they changed their mind`

**Failed hooks (self-focused):**
- "Why does my flat look like a student loan" → 905 views
- "See your room in 12+ styles before you commit" → 879 views

**Winning hooks (story-driven):**
- "My landlord said I can't change anything so I showed her what AI thinks" → 234K
- "I showed my mum what AI thinks our living room could be" → 167K
- "My landlord wouldn't let me decorate until I showed her these" → 147K

### Image Consistency
Lock room architecture across all 6 slides. Specify: dimensions, window count/position, door location, camera angle, furniture size, ceiling height, floor type. Only change the style (wall color, decor, lighting). Vague prompts = different rooms = looks fake.

### Image Specs
- 1024x1536 portrait (NOT landscape — causes black bars)
- Include "iPhone photo" and "realistic lighting" in prompts
- Add signs of life (mugs, remote control, TV) to "before" rooms
- Don't add people

### Text Overlays
- Font size 6.5% (not 5% — too small)
- Don't position too high (hidden behind TikTok status bar)
- Watch line length vs max width (prevents horizontal compression)

### Slideshow Format
- 6 slides exactly (TikTok sweet spot)
- Slide 1: hook text overlay
- Story-style caption relating to hook, mentions app naturally
- Max 5 hashtags

### Workflow
1. Agent generates images + text overlays + caption
2. Uploads to TikTok as draft via Postiz API (privacy_level: SELF_ONLY)
3. Sends caption to human via message
4. Human opens TikTok, adds trending sound, pastes caption, publishes

### Skills Used from ClawHub
- RevenueCat skill (by @jeiting) — subscription/churn analytics
- Bird skill (by @steipete) — browse X for trends

### What Failed
- Local Stable Diffusion: quality gap too large vs gpt-image-1.5
- Landscape images: black bars killed engagement
- Feature-focused hooks: nobody cares about your app's features
- Vague prompts: inconsistent rooms across slides
