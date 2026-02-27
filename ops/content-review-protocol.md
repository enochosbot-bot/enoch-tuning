# Content Review Protocol
Last Updated: 2026-02-27
Owners: Ezra (scribe), Solomon (solomon)

## Purpose
All content must pass strategic review before publishing. This prevents off-brand, poorly timed, or misaligned content from reaching audiences. Ezra writes, Solomon reviews, nothing ships without alignment.

---

## Flow

```
1. Content drafted (by Ezra, or dispatched to Ezra by Enoch)
2. Ezra saves draft → shared-context/drafts/{slug}.md
3. Ezra hands off to Solomon via sessions_send (CONTENT_REVIEW)
4. Solomon reviews against criteria below
5. Solomon writes feedback → shared-context/feedback/{slug}-review.md
6. Solomon hands back to Ezra via sessions_send (REVIEW_VERDICT)
7. If REVISE → Ezra incorporates feedback, loops back to step 3 (max 1 revision)
8. If APPROVE → Ezra publishes (dispatch to Bezzy for website, or post via script)
9. If KILL → Ezra notifies Deacon with Solomon's reasoning
10. Summary posted to Security & Ops (topic 3061) for visibility
```

---

## File Locations

| What | Path |
|---|---|
| Drafts | `shared-context/drafts/{slug}.md` |
| Review feedback | `shared-context/feedback/{slug}-review.md` |
| This protocol | `ops/content-review-protocol.md` |

### Slug Convention
Use lowercase, hyphenated: `linkedin-launch-week`, `spectrum-demo-blog`, `x-thread-ai-compliance`

---

## Ezra's Responsibilities (Pre-Review)

Before handing off to Solomon:
1. Save the draft to `shared-context/drafts/{slug}.md`
2. Include a frontmatter block at the top:

```markdown
---
title: [Post title]
platform: [linkedin | x | blog | website | newsletter]
audience: [who this is for]
goal: [what this should accomplish]
draft_version: 1
date: [YYYY-MM-DD]
---
```

3. Send a CONTENT_REVIEW handoff to Solomon:

```
HANDOFF: CONTENT_REVIEW
FROM: scribe
SLUG: {slug}
PLATFORM: {platform}
DRAFT_PATH: shared-context/drafts/{slug}.md
NOTES: [any context Solomon should know]
```

---

## Solomon's Review Criteria

Evaluate every draft against these five dimensions:

### 1. Brand Alignment
- Does it sound like Deacon / Ridley Research?
- Professional but human, not corporate
- Shows expertise without being preachy

### 2. Strategic Fit
- Does this advance a current priority? (Check shared-context/priorities.md)
- Does it support Spectrum demo prep, social launch, or credibility building?
- Is it worth the audience's attention right now?

### 3. Audience Match
- Is the tone right for the platform?
- LinkedIn = professional authority, X = punchy/opinionated, Blog = deep/structured
- Would the target reader care about this?

### 4. Timing
- Is this the right moment to publish this?
- Any conflicts with other content in flight?
- Does it align with launch sequencing?

### 5. Quality & Clarity
- Strong hook / opening line?
- Clear structure and flow?
- Effective CTA or closing?
- Any claims that need sourcing?

---

## Solomon's Verdict Format

Write feedback to `shared-context/feedback/{slug}-review.md`:

```markdown
---
slug: {slug}
reviewer: solomon
verdict: [APPROVE | REVISE | KILL]
date: [YYYY-MM-DD]
revision_round: [1 | 2]
---

## Verdict: [APPROVE | REVISE | KILL]

## Brand Alignment
[Score 1-5] — [Brief note]

## Strategic Fit
[Score 1-5] — [Brief note]

## Audience Match
[Score 1-5] — [Brief note]

## Timing
[Score 1-5] — [Brief note]

## Quality & Clarity
[Score 1-5] — [Brief note]

## Required Changes (if REVISE)
1. [Specific, actionable change]
2. [Specific, actionable change]

## Reasoning (if KILL)
[Why this shouldn't be published at all]
```

Then send REVIEW_VERDICT back to Ezra:

```
HANDOFF: REVIEW_VERDICT
FROM: solomon
SLUG: {slug}
VERDICT: [APPROVE | REVISE | KILL]
FEEDBACK_PATH: shared-context/feedback/{slug}-review.md
SUMMARY: [1-2 sentence summary of verdict reasoning]
```

---

## Ezra's Post-Review Responsibilities

### On APPROVE
1. Publish via appropriate channel:
   - Blog/website → dispatch to Bezzy (coder) with deploy instructions
   - LinkedIn/X → execute via social posting script or manual post
2. Post summary to Security & Ops (topic 3061):
   `✅ Published: {title} on {platform}. Solomon approved. Link: {url}`

### On REVISE
1. Read Solomon's feedback from `shared-context/feedback/{slug}-review.md`
2. Incorporate changes
3. Save updated draft to `shared-context/drafts/{slug}.md` (increment draft_version)
4. Hand off to Solomon again (same CONTENT_REVIEW format)
5. **Max 1 revision round.** If Solomon requests a second revision, escalate to Deacon:
   `⚠️ Content stuck in review: {slug}. Solomon requested 2nd revision. Need your call.`

### On KILL
1. Notify Deacon with Solomon's reasoning
2. Archive the draft (move to shared-context/drafts/archived/)
3. Post to Security & Ops: `❌ Killed: {title}. Reason: {summary}`

---

## Rules

- **No publishing without review.** Zero exceptions. If Solomon is unreachable, escalate to Enoch/Deacon.
- **Max 1 revision round.** Prevents infinite loops. Second revision = escalate to Deacon.
- **Solomon reviews strategy, not prose.** Don't wordsmith — evaluate fit. Trust Ezra's craft.
- **Ezra owns final polish.** After APPROVE, Ezra can make minor formatting/platform adjustments without re-review.
- **Both agents read this protocol.** If in doubt, re-read this file.
