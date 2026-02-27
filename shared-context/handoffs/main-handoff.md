# Handoff — Enoch (main agent)
_Written: 2026-02-26 21:50 CST_

## Active Task
Getting X pinned post live. Blocked on OAuth 1.0a not being enabled in the RR.AI app settings after Consumer Key regeneration.

## Progress

### Done this session
- [x] 5 RIA-focused X posts deleted (tweet IDs confirmed deleted)
- [x] X Batch 2 rewritten around LEVERAGE positioning (bootstrappers/solo operators)
- [x] LinkedIn Batch 2 rewritten with same leverage angle
- [x] Pitch/pinned post copy written for both X and LinkedIn
- [x] Reply playbook written (7 sets, contrarian angle, whale account targets)
- [x] Financial advisor blog post noindexed, removed from blog index
- [x] Site deployed to CF Pages
- [x] Ridley Research ICP locked: bootstrapping small businesses & individuals, LEVERAGE frame
- [x] MiniMax API key stored in Keychain as `MINIMAX_API_KEY`
- [x] Shorty upgraded to gpt-4o for title generation
- [x] X Consumer Keys regenerated to: `bhWriU3i8D7LGf6GdFZTkh3P9` / `2dyGGarKfHeAB8JW0KrMpD1p9sI5zQUAZ3LiFw6Xcua2jRYscW`
- [x] X Access Tokens regenerated to: `2026169983705731072-ykVVdQjxsdTAxsv35nd9keIA0dXZXN` / `sj6q9kJuuV7nLIxWm8xutpxR8djtHgwuiLky4tw0fEIUL`
- [x] All 4 new X credentials stored in Keychain under `enoch_pro`

### Blocked
- [ ] **X pinned post**: OAuth 1.0a not enabled on RR.AI app — all API calls returning 401. Deacon needs to enable it in developer portal.

## Next Steps

### IMMEDIATE (first thing next session)
1. **Check if Deacon enabled OAuth 1.0a** — ask if he completed the setup step
2. **If yes**: Regenerate Access Token + Secret one more time, update Keychain, fire the pinned post + pin it
3. **Fire the pinned post copy** (ready in `research/social-drafts/queue/x-pitch-post.md`):
```
Most people running a business spend hours every week on work they hate and are bad at.

Admin. Follow-up. Proposals. Scheduling. The stuff that doesn't need your brain — it just needs to happen.

We build AI agents that handle that layer. Persistent. Autonomous. Built around how you actually work.

You stop doing the work that was in the way. You do more of the work only you can do.

That's the leverage play. That's what we build.

→ ridleyresearch.com
```
4. Pin it using `client.pin_tweet(tweet_id)`
5. **LinkedIn pinned post**: Token still revoked — need fresh OAuth before LinkedIn post fires. Script: `python3 scripts/linkedin-oauth.py` (port 8082), open URL in Mac mini browser.
6. **After both pinned posts live**: Start firing reply batches from `research/social-drafts/queue/x-replies-batch1.md`

### THEN
- OBA forms: still need LLC address, formation date, hours/month from Deacon → fill pages 14-17 of `/tmp/spectrum-forms/access-person-2026.pdf`
- Ezra's BL-003 LinkedIn posts: RIA-focused, trash them, use `linkedin-batch2.md` instead
- Cloudflare Zone Rules API token: need token with redirect/transform rule permissions

## Key Context

### X / @ridleyresearch
- **Status**: OAuth 1.0a BROKEN — 401 on all calls
- **Root cause**: Consumer Key regenerated, OAuth 1.0a User Auth Settings need re-save in portal
- **Fix**: App Settings → User authentication settings → Set up → OAuth 1.0a ON, Read+Write, callback=http://localhost, website=https://ridleyresearch.com → Save → Regenerate Access Token+Secret
- **Current Consumer Key**: `bhWriU3i8D7LGf6GdFZTkh3P9` (Keychain: `x_api_key`, account: `enoch_pro`)
- **Current Consumer Secret**: `2dyGGarKfHeAB8JW0KrMpD1p9sI5zQUAZ3LiFw6Xcua2jRYscW` (Keychain: `x_api_secret`)
- **Current Access Token**: `2026169983705731072-ykVVdQjxsdTAxsv35nd9keIA0dXZXN` (Keychain: `x_access_token`)
- **Current Access Token Secret**: `sj6q9kJuuV7nLIxWm8xutpxR8djtHgwuiLky4tw0fEIUL` (Keychain: `x_access_token_secret`)
- **X post script**: `scripts/x-post.py` (tweepy, OAuth 1.0a)
- **Pinned post copy**: `research/social-drafts/queue/x-pitch-post.md`
- **Reply playbook**: `research/social-drafts/queue/x-replies-batch1.md`
- **Batch 2 posts**: `research/social-drafts/queue/x-batch2-bootstrappers.md` (leverage angle, awaiting approval)

### LinkedIn
- **Status**: Token REVOKED — needs re-auth
- **OAuth script**: `scripts/linkedin-oauth.py` (port 8082) — updated with `w_organization_social` scope
- **Pinned post copy**: `research/social-drafts/queue/linkedin-pitch-post.md`
- **Batch 2 posts**: `research/social-drafts/queue/linkedin-batch2.md` (leverage angle)
- **Trash**: `shared-context/drafts/linkedin-launch-week.md` from Ezra — RIA focused, wrong ICP
- **Member ID**: `zdRbe2RHRF` | Client ID: `869fp76go0gr0x`

### Content Strategy (LOCKED)
- **ICP**: Bootstrapping small businesses & individuals
- **Core concept**: LEVERAGE — convert bad hours (things you hate/are bad at) into high-value output
- **NOT**: RIAs, financial services, enterprise, regulated industries
- **Tone**: Contrarian, direct, dry. Pushback on whale takes = profile clicks
- **Whale targets**: @levelsio, @dhh, @naval, @sama, @paulg, @GergelyOrosz
- **Flow**: Deacon drops whale post URL → I customize reply → Deacon approves → fires

### Site
- **Live**: ridleyresearch.com → Cloudflare Pages (`ridleyresearch`)
- **Deploy**: `wrangler pages deploy . --project-name ridleyresearch` from `ridleyresearch-site-v2-revamped/ridleyresearch-site-v2/`
- **Financial advisor post**: noindexed, removed from blog index ✅

### Keys Added This Session
- `MINIMAX_API_KEY`: `sk-api-1_aELlNHi...` (stored Keychain) — wired into `scripts/vidgen.py`
- `X_OAUTH2_CLIENT_SECRET`: `Qu9_PZVBu3CRS_...` (stored Keychain) — not currently used

## Blockers
1. **X OAuth 1.0a**: Deacon must enable in developer portal (App Settings → User auth settings)
2. **LinkedIn token**: Revoked — need browser OAuth on Mac mini
3. **OBA forms**: Need LLC address, formation date, hours/month from Deacon
4. **MiniMax key rotation**: Was sent in Telegram plaintext — recommend rotation
