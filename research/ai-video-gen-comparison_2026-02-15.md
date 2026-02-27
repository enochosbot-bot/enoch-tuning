# AI Video Generation Model Comparison (API-focused) — Feb 15, 2026

> Scope requested: MiniMax Hailuo 2.3, Seedance 2.0, Kling, WAN, Google Veo, OpenAI Sora, Runway, Pika + notable alternatives.
> 
> **Important:** pricing and rankings change fast; dynamic pages often hide exact prices. I prioritized official docs and provider model pages where possible, then marked lower-confidence items.

## Executive summary (best quality-to-cost right now)

**Best quality-to-cost (API, Feb 2026):**
1. **MiniMax Hailuo 2.3 / 2.3 Fast** — strong quality at very low effective cost (~$0.03–$0.09/s depending tier/resolution).
2. **Kling (2.6 Pro on API providers)** — very strong quality + audio at ~$0.07/s (no audio) / ~$0.14/s (audio).
3. **Runway Gen4 Turbo** — reliable production API at **$0.05/s**, but quality usually below top premium tiers.
4. **WAN (Alibaba wan2.2-s2v)** — cost-efficient in official cloud for specific workflows (~$0.072/s 480p, ~$0.129/s 720p).
5. **Veo 3 Fast / Sora 2 Standard** — high quality but pricier than Hailuo/Kling for volume, especially with audio.

If optimizing for **absolute quality** (not cost): Veo 3.1 / Sora 2 Pro / top Seedance variants / latest Kling Pro generally lead, but with materially higher spend.

---

## Comparison table

| Model | Pricing (USD) | Approx $/sec | Quality rank (Feb 2026) | API availability | Resolution options | Free tier / credits |
|---|---:|---:|---|---|---|---|
| **MiniMax Hailuo 2.3** | MiniMax unit-based (see below) | ~**$0.042–0.089/s** (derived) | **Top tier** (frequently benchmarked near top) | **Yes** (MiniMax API; also aggregators) | 768p, 1080p (and 512p for Hailuo-02 configs) | No persistent free tier found; package-based billing |
| **MiniMax Hailuo 2.3 Fast** | 0.7 unit (768p 6s), 1.1 unit (768p 10s), 1.3 unit (1080p 6s) | ~**$0.029–0.058/s** (derived) | High | Yes | 768p, 1080p | Same as above |
| **Seedance 2.0** | **Official API price not clearly published yet** in accessible official docs | N/A (insufficient official pricing) | **Top tier** (widely cited as leading quality) | Partial/rolling (official + partner access appears in progress) | Common claims: up to 2K, multimodal refs (verify in official release docs) | Varies by channel; some partner trial credits reported |
| **Kling 2.6 Pro** | $0.07/s (audio off), $0.14/s (audio on) | **$0.07–0.14/s** | **Top tier** | Yes (official dev + aggregators) | Typically 5s/10s clips; 720p/1080p variants on related endpoints | Some providers offer free preview credits |
| **WAN (Alibaba wan2.2-s2v)** | 480p: $0.071677/s, 720p: $0.129018/s | **$0.072–0.129/s** | Mid-to-high (strong for cost/open ecosystem) | Yes (DashScope/Model Studio) | 480p, 720p (model-specific) | Alibaba notes free quota consumed first (region/model dependent) |
| **Google Veo 3 Fast** | $0.25/s (audio off), $0.40/s (audio on) | **$0.25–0.40/s** | **Very high / premium** | Yes (Vertex + partner APIs) | Provider-dependent (often HD tiers, audio variants) | Google ecosystem often has trial credits; verify account-level offers |
| **OpenAI Sora 2 (standard)** | $0.10/s (via partner billing statement) | **$0.10/s** | **Very high / premium** | Yes (partner + direct API charging flows) | 720p/1080p depending tier | Launch/free access has existed in product tiers; API free usage not assumed |
| **OpenAI Sora 2 Pro** | $0.30/s (720p), $0.50/s (1080p) | **$0.30–0.50/s** | **Top premium** | Yes | 720p, 1080p; up to 25s on cited endpoint | No general API free tier assumed |
| **Runway Gen4** | 12 credits/s @ $0.01/credit | **$0.12/s** | High | Yes (Runway API) | Model-specific; Gen4 family supports HD workflows | Account signup; no broad permanent free API tier noted |
| **Runway Gen4 Turbo** | 5 credits/s @ $0.01/credit | **$0.05/s** | High-mid (vs top premium) | Yes | Same family; faster/cheaper path | Same as above |
| **Pika (consumer + API ecosystem)** | Official public API docs found for keys; clear **video $/sec** not consistently published in official docs scraped | N/A / credit-based | Mid-to-high (strong for social/effects) | Yes (API exists) | Varies by model tier (commonly 480p/720p/1080p in market) | Free consumer credits commonly exist; API plans are separate |
| **Haiper Video 2.x** *(extra)* | 720p: $0.05/s, 540p: $0.033/s | **$0.033–0.05/s** | Mid-to-high | Yes | 540p, 720p | No universal free tier specified |
| **PixVerse v5.6** *(extra)* | Credit-based; doc gives conversion $1=100 credits and per-clip credit matrix | e.g. ~**$0.07/s** for 540p 5s no-audio (35 credits) | Mid-to-high | Yes | 360p/540p/720p/1080p (model/duration dependent) | Tiered memberships + purchased credits |
| **Luma Ray family** *(extra)* | Credit-based subscription system (web/app + separate API credits) | Depends on plan/model; can be competitive at lower tiers | High-mid | Yes (separate API billing track) | Up to 4K (up-res/HDR on higher plans) | Free plan available in product; API credits separate |

---

## MiniMax Hailuo 2.3 cost derivation (why it lands at ~$0.25–0.30/video)

From MiniMax video packages:
- Standard package: $1000 / 3760 units = **$0.266/unit**
- Pro package: $2500 / 9920 units = **$0.252/unit**

From MiniMax deduction rules:
- Hailuo 2.3 (768p, 6s) = **1 unit** ⇒ **$0.252–$0.266/video**
- Hailuo 2.3 (768p, 10s) = **2 units** ⇒ **$0.504–$0.532/video**
- Hailuo 2.3 Fast (768p, 6s) = **0.7 unit** ⇒ **$0.176–$0.186/video**

This matches your target range for standard 6s jobs and explains why Fast is often the best batch-value option.

---

## Quality ranking (practical, API buyer view)

### Tier S (best raw quality / realism / coherence)
- **Seedance 2.0** (where available)
- **Sora 2 Pro**
- **Veo 3.1 / Veo 3 premium variants**
- **Hailuo 2.3 / Hailuo 02 high-tier**
- **Kling latest Pro tiers**

### Tier A (strong quality, better economics)
- **Runway Gen4 / Gen4 Turbo**
- **WAN 2.2+ family**
- **Luma Ray3 family**
- **PixVerse 5.x**
- **Pika 2.x**
- **Haiper 2.x**

**Best quality/$ among Tier-S-ish outputs:** Hailuo 2.3 Fast / Kling Pro (no-audio path) are currently hard to beat for volume production.

---

## Notes by requested model

### 1) MiniMax Hailuo 2.3
- **API:** Yes (official MiniMax + partner APIs)
- **Pricing:** Unit-based; effective ~$0.25–0.30 for a 6s 768p standard generation.
- **Resolutions:** 768p, 1080p (and some 512p configs on Hailuo-02)
- **Free tier:** Not clearly persistent; package model dominates.

### 2) Seedance 2.0
- **API:** Appears rolling/region/partner dependent; official accessible pricing still inconsistent in public docs.
- **Pricing:** Insufficient official public numbers for reliable $/sec in this pass.
- **Resolutions:** Reported up to 2K in multiple secondary sources.
- **Free tier:** Varies by distribution channel.

### 3) Kling
- **API:** Yes.
- **Pricing:** Competitive in partner APIs (~$0.07/s no audio; ~$0.14/s with audio on cited 2.6 Pro endpoint).
- **Resolutions:** Typically 720p/1080p depending endpoint/version.
- **Free tier:** Often preview credits on partner platforms.

### 4) WAN
- **API:** Yes (Alibaba Model Studio / DashScope).
- **Pricing:** Official per-second pricing found for wan2.2-s2v.
- **Resolutions:** 480p/720p in that model.
- **Free tier:** Free quota then PAYG (per Alibaba doc).

### 5) Google Veo
- **API:** Yes (official cloud + partner APIs).
- **Pricing:** Premium; cited fast path at $0.25–$0.40/s.
- **Resolutions:** HD/premium tiers vary by endpoint.
- **Free tier:** Cloud trial credits may apply; not guaranteed ongoing free API.

### 6) OpenAI Sora
- **API:** Yes (direct-key pass-through supported on partner endpoints).
- **Pricing:** Standard around $0.10/s; Pro tiers up to $0.50/s at 1080p.
- **Resolutions:** 720p/1080p on cited endpoint.
- **Free tier:** Product-side free exploration has existed; API free quota not assumed.

### 7) Runway
- **API:** Yes, very mature.
- **Pricing:** Clear credits model with fixed $0.01/credit; Gen4 Turbo cost-efficient at $0.05/s.
- **Resolutions:** Depends on model endpoints and workflow.
- **Free tier:** API usually paid usage; app-side plans/credits differ.

### 8) Pika
- **API:** Yes (official API docs for key provisioning).
- **Pricing:** Video API $/sec difficult to confirm from official docs scraped; mostly credit-plan marketing surfaced.
- **Resolutions:** Model dependent; common tiers include 480p/720p/1080p.
- **Free tier:** Consumer free credits widely offered; API usage is paid plans.

---

## Source links (key)

- MiniMax video pricing/deductions: https://platform.minimax.io/docs/guides/pricing-video
- Runway API pricing (credits/s): https://docs.dev.runwayml.com/guides/pricing/
- Kling pricing example endpoint: https://fal.ai/models/fal-ai/kling-video/v2.6/pro/image-to-video
- Veo 3 Fast pricing endpoint: https://fal.ai/models/fal-ai/veo3/fast
- Sora 2 standard endpoint note: https://fal.ai/models/fal-ai/sora-2/text-to-video
- Sora 2 Pro endpoint: https://fal.ai/models/fal-ai/sora-2/text-to-video/pro
- Alibaba WAN (wan2.2-s2v) official pricing: https://www.alibabacloud.com/help/en/model-studio/wan-s2v-api
- Haiper API pricing: https://docs.haiper.ai/api-reference/api-pricing
- PixVerse model pricing: https://docs.platform.pixverse.ai/model-pricing-796039m0
- Luma plans/credit system: https://lumalabs.ai/pricing and https://lumalabs.ai/learning-hub/dream-machine-support-pricing-information
- Artificial Analysis model/leaderboard index: https://artificialanalysis.ai/video/models and https://artificialanalysis.ai/video/leaderboard/text-to-video

---

## Confidence / caveats

- **High confidence:** MiniMax, Runway, WAN, Haiper, PixVerse numeric pricing rows (direct docs).
- **Medium confidence:** Kling/Veo/Sora prices from partner model pages (credible but not always official first-party list price).
- **Low-to-medium confidence:** Seedance 2.0 exact API pricing (official public data still fragmented at query time).

If you want, I can do a **phase-2 pass** that normalizes every model to a single benchmark scenario (e.g., 5s 720p no-audio + 10s 1080p with audio) and provide a strict ranked scorecard (Quality × Cost × API maturity).