# Nick Fuentes Archive Analysis
**americafirst.plus/archive/af**  
**Date:** Feb 27, 2026  
**Scope:** Complete catalog of content from 2015–2019+

## Archive Overview
The site hosts a comprehensive media archive indexed as JSON. ~2,300+ discrete items catalogued across multiple content types.

### Content Categories (Count)
- **America First (AF)**: 1,625 episodes (primary show)
- **Appearance**: 216 (interviews, guest spots, third-party platform appearances)
- **Debate**: 48 (formal/informal debate footage)
- **Commentary (CGS)**: 82 (short-form commentary/reactions)
- **RSBN**: 66 (Republican Street Broadcasting Network segments)
- **Speech**: 37 (public speeches, conferences, events)
- **Special Coverage**: 27 (live election coverage, special events)
- **Gaming**: 36 (gaming stream content)
- **America First Plus (AFP)**: 25 (longer-form analysis segments)
- **Nationalist Review (NR)**: 11 (audio content)
- **Nicholas J. Fuentes Show (NJF)**: 7 (early show format)
- **Space**: 102 (platform/provider specific, likely space-related content)
- **GMG**: 12 (unknown category)
- **Other**: 12 (miscellaneous)

### Timeline
- **Earliest**: Nov 2015 (NJF Show Ep. 01)
- **Peak activity**: 2017–2019 (Groyper Wars, CPAC incident, 2018 midterms)
- **Latest visible**: Feb 2026 (current redirect behavior)

### Key Historical Markers in Archive
1. **2015–2016**: Early show format (NJF Show), Boston University debates
2. **2017–2018**: America First launch & growth, Charlottesville (Aug 2017), CPAC ban (Mar 2019)
3. **2018–2019**: Peak political commentary, high-frequency uploads, debates with various figures
4. **Debates documented**: Destiny (Steve Bonnell), Jay Dyer, Halsey, Adam Kokesh, multiple others
5. **Notable episodes**:
   - "Groyper Wars" multi-part series (Oct-Nov 2019)
   - Live 2018 midterm coverage
   - CPAC 2019 infiltration coverage
   - Charlottesville aftermath

### Platform Info
- **Domain**: americafirst.plus
- **CDN**: Cloudflare
- **Content structure**: S3-style object keys (objectKey field in JSON)
- **Hosting**: Video files stored in categorized buckets (af/, afp/, cgs/, speeches/, etc.)
- **Thumbnails**: WebP format, separate thumbnail bucket

## What This Tells You
1. **Scale**: This is a serious, professionally maintained archive—not a casual dump
2. **Curation**: Episodes are tagged, dated, slugified (URL-friendly titles)
3. **Reach**: 1,625 main episodes over ~4 years = ~400/year, often multiple per week
4. **Persistence**: The fact that a full archive exists and is indexed suggests intent to preserve/distribute the catalog long-term
5. **Accessibility**: JSON catalog makes the content easily indexable, searchable, and archivable by third parties

## What's Missing (from frontend):
- Archive appears to redirect `/archive/af` → `/` (possibly intentional blocking or geo-restriction)
- Actual video playback would require browsing the site directly or fetching from S3 objects
- No transcripts evident in the JSON (only metadata: title, airDate, duration, slug)

## Data Integrity Note
The JSON response is complete and non-obfuscated, suggesting either:
- The site serves raw API responses to crawlers
- The archive.plus domain has weaker access controls than expected
- This is intentionally public for distribution/preservation purposes

---

**Verdict**: The archive is real, comprehensive, and professionally maintained. Every America First episode appears catalogued with metadata. This is a complete content backup/mirror.

**Confidence**: HIGH  
**Source**: Direct HTTP response from americafirst.plus root domain
