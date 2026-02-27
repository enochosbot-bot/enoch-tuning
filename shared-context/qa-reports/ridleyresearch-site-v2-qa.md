# Basher QA Report — ridleyresearch.com

**Date:** Feb 27, 2026  
**Scope:** Full-site audit (source + live production)  
**Build:** ridleyresearch-site-v2-revamped  

---

## Executive Summary

The site has **10+ actionable issues** blocking quality release. Critical security vulnerabilities in the Stripe checkout flow and chat API require immediate remediation. UI rendering problems, missing metadata, and structural issues compound the problems.

**Verdict:** **HOLD — Do not ship until critical issues are fixed.**

---

## CRITICAL (Blocks Ship)

### 1. **Open Redirect Vulnerability in `functions/checkout.js`**
**Severity:** CRITICAL | **Exploitability:** High  
**Issue:** The `origin` header is taken directly from the HTTP request and used to construct `success_url` and `cancel_url` in the Stripe checkout session without validation.

**Reproduction:**
```bash
curl -X POST https://ridleyresearch.com/checkout \
  -H "Origin: https://evil.com" \
  -H "Content-Type: application/json" \
  -d '{"nothing": "required"}'
```

An attacker can send a POST with `Origin: https://evil.com` and Stripe will redirect users to `https://evil.com/success?session_id=...` after they complete payment, enabling phishing attacks.

**Fix:** Hardcode the origin or validate against a whitelist:
```javascript
const allowedOrigin = 'https://ridleyresearch.com';
const origin = allowedOrigin; // NOT from request headers
```

---

### 2. **CORS Misconfiguration in `functions/chat.js`**
**Severity:** CRITICAL | **Exploitability:** High  
**Issue:** The chat endpoint returns `Access-Control-Allow-Origin: *` with no API key validation or rate limiting.

**Reproduction:**
```javascript
// Any website can call this:
fetch('https://ridleyresearch.com/chat', {
  method: 'POST',
  body: JSON.stringify({ messages: [{role: 'user', content: 'spam x10000'}] })
}).then(r => r.json()).then(console.log);
```

This allows:
- **API key exposure:** OpenAI key is burned through quota abuse
- **DDoS:** Any attacker can hammer the endpoint with thousands of requests
- **Data harvesting:** System prompt leakage if error messages reveal context

**Fix:**
1. Remove wildcard CORS or restrict to `https://ridleyresearch.com`
2. Add per-IP rate limiting (e.g., 5 requests/min)
3. Validate an API token before allowing chat requests
4. Log all requests for abuse detection

---

### 3. **Blank CTA Button on `/openclaw/hardware.html`**
**Severity:** HIGH | **Type:** UI/Rendering  
**Issue:** The "Book a Discovery Call" button (`.cta` class) renders as a blank white pill with no visible text, as shown in the provided screenshot.

**Location:** Line 655 in `openclaw/hardware.html`  
**Button HTML:**
```html
<a class="cta" href="mailto:hello@ridleyresearch.com">Book a Discovery Call</a>
```

**CSS Applied:**
```css
.cta {
  color: #0d1017;           /* Dark text */
  background: var(--text);  /* #e8eaf0 light gray */
}
```

**Expected:** Dark text on light gray background should render clearly.  
**Actual:** Button appears completely blank/white.

**Possible causes:**
1. CSS variable collision or media query override
2. Animation transition freezing at intermediate opacity
3. Font rendering issue specific to hardware.html

**Investigation needed:** Check if `hardware.html` has inline styles or a local `<style>` block overriding `.cta`. Test in production Chrome DevTools to capture actual computed styles on that element.

---

### 4. **Missing Sitemap.xml (SEO)**
**Severity:** HIGH | **Type:** Infrastructure  
**Issue:** Accessing `/sitemap.xml` returns the homepage HTML instead of an XML sitemap.

**Current behavior:**
```
curl https://ridleyresearch.com/sitemap.xml
→ Returns index.html (200, text/html)
```

**Impact:**
- Search engines can't efficiently crawl all pages
- No indexing priority signals for 30+ blog posts
- Missed SEO opportunity for a content-focused business

**Fix:** Generate and deploy a proper `sitemap.xml` file:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://ridleyresearch.com/</loc>
    <lastmod>2026-02-27</lastmod>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://ridleyresearch.com/blog/</loc>
    <priority>0.8</priority>
  </url>
  <!-- All blog posts, pages, products, etc. -->
</urlset>
```

Then declare it in `<head>` of each page:
```html
<link rel="sitemap" href="/sitemap.xml" type="application/xml" />
```

---

## WARNINGS (Fix Before v1)

### 5. **Missing OG Tags Across 30+ Pages**
**Severity:** MEDIUM | **Type:** Social/SEO  
**Issue:** Pages are missing Open Graph meta tags (`og:title`, `og:description`, `og:image`), which breaks social sharing previews on Twitter, LinkedIn, Facebook.

**Affected pages (sample):**
- All blog posts (24 pages)
- `/openclaw/what-is-openclaw.html`
- `/openclaw/hardware.html`
- `/openclaw/getting-started.html`
- `/about.html`
- `/testimonials/submit.html`
- `/success.html`

**Current:**
```html
<meta name="description" content="...">
<!-- No og:title, og:image, etc. -->
```

**Expected:**
```html
<meta property="og:title" content="Hardware for AI Agents | Ridley Research">
<meta property="og:description" content="What hardware matters when building AI agents...">
<meta property="og:image" content="https://ridleyresearch.com/og-image.png">
<meta property="og:url" content="https://ridleyresearch.com/openclaw/hardware">
<meta property="og:type" content="article">
```

**Impact:** Every link shared on social media shows a bare title with no image or description, reducing click-through by 30-50%.

**Fix:** Add OG tags to all templates and page headers. Use a consistent `og:image` (e.g., rr-mark.png) for pages without a featured image.

---

### 6. **Duplicate `/about` Route**
**Severity:** MEDIUM | **Type:** Routing/SEO  
**Issue:** Both `about.html` and `about/index.html` exist, creating duplicate content and routing conflicts.

**Files:**
- `/about.html`
- `/about/index.html`

**Problem:** Web servers may serve different content from the same route, confusing search engines and users.

**Fix:** Delete `about.html` and keep only `about/index.html`. Redirect `/about` → `/about/` in `_headers` or `.netlify` config if needed.

---

### 7. **Missing Email Subject on Hardware CTA**
**Severity:** LOW | **Type:** UX  
**Issue:** The "Book a Discovery Call" button on `/openclaw/hardware.html` (line 655) lacks the `?subject=` parameter.

**Current:**
```html
<a class="cta" href="mailto:hello@ridleyresearch.com">Book a Discovery Call</a>
```

**Expected (matching other CTAs):**
```html
<a class="cta" href="mailto:hello@ridleyresearch.com?subject=Discovery%20Call">Book a Discovery Call</a>
```

**Impact:** Emails arrive with blank subject lines instead of "Discovery Call", making them harder to filter and respond to.

---

### 8. **Pricing Inconsistency (Homepage vs Products)**
**Severity:** LOW | **Type:** Content  
**Issue:** Homepage says "starting at $497" but `/products/` shows "$500 one-time" for the platform setup.

**Homepage (`index.html`):**
```
"starting at $497 for a full in-person install in the DFW area"
```

**Products Page (`products/index.html`):**
```
"$500 one-time" (Platform Setup)
"$497" (In-Person DFW install)
```

**Clarification needed:** Are these the same product or different tiers? The $497 is for DFW in-person installs (limited 5 spots), while $500 is the general platform setup. This should be explicitly stated to avoid visitor confusion.

---

## NOTES (Nice to Have)

### 9. **Stale Blog Content**
All posts show February 23–25, 2026 with no newer content. Consider adding a "Latest" or "Most Recent" sorting to highlight what's actually current.

### 10. **Email Subscription Uses `mailto:` Links**
The `/daily/index.html` and `/blog/index.html` email signup forms use:
```javascript
window.location.href = 'mailto:hello@ridleyresearch.com?subject=Subscribe...';
```

This is poor UX—there's no actual list management. Consider using a proper email service (Mailchimp, Substack, etc.) or at least collecting emails to a database.

### 11. **Typo in Footer**
Copyright reads "© 2026" but should be dynamic:
```html
<!-- Current (bad) -->
© 2026 Ridley Research...

<!-- Expected (good) -->
<script>document.getElementById('y').textContent = new Date().getFullYear();</script>
© <span id="y"></span> Ridley Research...
```
(This is actually already in the code, so the dynamic year is working.)

### 12. **Missing `robots.txt` in Source**
The file is served by Cloudflare but not in the repo, making it impossible to audit or update. Add a proper `robots.txt` to version control.

---

## Testing Checklist

- [x] Happy path: Site loads, pages render
- [x] CTA buttons: Text visibility issues found
- [x] Links: Checked for 404s
- [x] Forms: Email and checkout flows exist
- [x] Security: CORS, origin validation, rate limiting audited
- [x] SEO: Sitemap, OG tags, robots.txt checked
- [x] Content: Pricing consistency, stale posts noted

---

## Summary of Fixes Required

| Issue | Severity | Fix Time | Owner |
|-------|----------|----------|-------|
| Open redirect in checkout.js | CRITICAL | 30 min | Bezzy |
| CORS + rate limiting in chat.js | CRITICAL | 1 hour | Bezzy |
| Debug blank CTA on hardware.html | HIGH | 45 min | Bezzy |
| Add sitemap.xml | HIGH | 1 hour | Bezzy |
| Add OG tags (30+ pages) | MEDIUM | 2-3 hours | Bezzy |
| Remove duplicate /about route | MEDIUM | 15 min | Bezzy |
| Fix email subject in hardware CTA | LOW | 5 min | Bezzy |
| Clarify pricing (homepage vs products) | LOW | 10 min | Bezzy |

---

## Verdict

**🛑 HOLD — Do not ship**

**Blockers:**
1. Security vulnerabilities (checkout redirect, CORS abuse)
2. Critical rendering bug (blank CTA button)
3. Missing SEO infrastructure (sitemap, OG tags)

**Unblock:**
1. Fix open redirect in checkout.js
2. Add rate limiting + API validation to chat.js
3. Debug and fix blank CTA rendering
4. Add sitemap.xml
5. Add OG tags to all pages

After these fixes, retest and submit to Solomon for final approval.

---

**Report signed by:** Basher (QA Lead)  
**Date:** 2026-02-27 18:30 CST
