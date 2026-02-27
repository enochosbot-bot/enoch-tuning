---
title: FEC Donor Data + Texas Ethics Cross-Referencing Tooling — Specification
task: BL-012
author: Ezra (research subagent)
date: 2026-02-27
status: READY FOR DEACON REVIEW
prior_work: BL-006 (texas-donors-run3), openplanter-runs findings.md
---

# FEC + Texas Ethics Cross-Reference Tooling — Spec

## Executive Summary

This spec covers everything Bezzy needs to build a Texas political donor → officeholder → influence database. FEC federal data is fully public, well-documented, and available via REST API or bulk download at zero cost. Texas Ethics Commission (TEC) state data is also free but requires bulk CSV export — no API exists. The cross-reference joins on donor name + address + employer across both datasets. A working MVP can be built in ~5 hours using SQLite + Python. The first high-value investigation target is Ken Paxton's 2026 Senate donor network (FEC committee C00901918) mapped against TEC state-level giving.

Data gap identified in BL-006: `indiv26.zip` (FEC individual contributions, ~4–6GB) was not downloaded. Both download path and API alternative are documented below.

---

## 1. FEC Data Access

### 1.1 Bulk Downloads

**Base URL pattern:** `https://www.fec.gov/files/bulk-downloads/{YEAR}/`

All files are pipe-delimited text (`.txt`) inside zip archives. Header rows are **not included** — field order is documented in FEC's data dictionaries at `fec.gov/campaign-finance-data/`.

| File | Filename | Approx Size (2026) | Contents | Priority |
|------|----------|--------------------|----------|----------|
| Candidate Master | `cn26.zip` | ~800KB | All registered federal candidates with status, office, party, state, district | ✅ Already in workspace |
| Committee Master | `cm26.zip` | ~2.5MB | All PACs, campaign committees, party orgs | ✅ Already in workspace |
| Candidate-Committee Linkage | `ccl26.zip` | ~200KB | JOIN table: candidate_id ↔ committee_id | Download |
| **Individual Contributions** | **`indiv26.zip`** | **~4–6GB** | **Every itemized donation from an individual: name, address, employer, amount, date, candidate** | **⚠️ CRITICAL MISSING** |
| PAC-to-Candidate Contributions | `pas226.zip` | ~250MB | Committee-to-committee money flows | Download |
| Operating Expenditures | `oppexp26.zip` | ~600MB | Campaign spending by purpose and vendor | Download if needed |
| Candidate Summary | `weball26.zip` | ~60MB | Top-line fundraising totals per candidate per cycle | Download |
| Independent Expenditures | `indexp26.zip` | ~150MB | Super PAC spending for/against candidates | Optional |

**Direct download URLs (2026 cycle):**
```
https://www.fec.gov/files/bulk-downloads/2026/cn26.zip
https://www.fec.gov/files/bulk-downloads/2026/cm26.zip
https://www.fec.gov/files/bulk-downloads/2026/ccl26.zip
https://www.fec.gov/files/bulk-downloads/2026/indiv26.zip    ← GET THIS
https://www.fec.gov/files/bulk-downloads/2026/pas226.zip
https://www.fec.gov/files/bulk-downloads/2026/weball26.zip
```

**How to get just Texas from indiv26.zip without downloading 6GB:**
Use the REST API (Section 1.2) with `contributor_state=TX` — returns only TX-address donors. This is the recommended approach. Bulk download only needed for offline/comprehensive analysis.

**Update frequency:** Bulk files refresh daily (business days). Updated ~48h after filings received.

**File format detail:**
- Pipe-delimited: `|` as separator
- No header row — field order defined by FEC data dictionaries
- Encoding: UTF-8 (mostly ASCII in practice)
- FEC provides `.fec` header files documenting field positions per file type

### 1.2 FEC REST API (OpenFEC)

**Base URL:** `https://api.open.fec.gov/v1/`

**API key:** Free, instant at `https://api.data.gov/signup/`. Use `DEMO_KEY` for testing (rate-limited: 30 req/hr). With key: 1,000 req/hr.

**Interactive docs / Swagger UI:** `https://api.open.fec.gov/developers/`

**Key endpoints for this project:**

| Endpoint | Purpose | Key Filters |
|----------|---------|-------------|
| `GET /candidates/` | Search candidates | `office`, `state`, `cycle`, `party` |
| `GET /candidate/{id}/` | Single candidate details | — |
| `GET /committees/` | Search PACs + committees | `state`, `committee_type`, `designation` |
| `GET /committee/{id}/totals/` | Fundraising totals | `cycle` |
| `GET /schedules/schedule_a/` | **Individual contributions** | `contributor_state`, `candidate_office_state`, `two_year_transaction_period`, `contributor_zip`, `min_amount`, `max_amount` |
| `GET /schedules/schedule_b/` | Disbursements/expenditures | `recipient_state`, `two_year_transaction_period` |
| `GET /schedules/schedule_e/` | Independent expenditures | `candidate_id`, `cycle` |

**TX-specific filter examples:**
```
# All TX-address individual donors to federal candidates, 2026 cycle
GET /schedules/schedule_a/?contributor_state=TX&two_year_transaction_period=2026&api_key=YOUR_KEY

# All donations to Ken Paxton's Senate committee
GET /schedules/schedule_a/?committee_id=C00901918&two_year_transaction_period=2026&api_key=YOUR_KEY

# DFW-area donors (zip prefix filter — API doesn't support prefix, use min/max range)
# Zips 75001–75099 cover Dallas; 75201–75399 cover Dallas city; 760xx covers Fort Worth
```

**Pagination:** All endpoints return `pagination.count` and `pagination.pages`. Use `page=N` and `per_page=100` (max). Expect 500–5,000 pages for full TX Schedule A pull.

**Rate limit strategy:** With key, 1,000 req/hr = ~16 req/min. For full TX pull (~50,000 TX donors in 2026 cycle at 100/page = 500 pages), takes ~30 minutes.

### 1.3 PII Considerations

Per 52 U.S.C. § 30111(a)(4): "Individual contributor names and addresses may not be sold or used by any person for the purpose of soliciting contributions or for commercial purposes."

**Permissible uses:** Investigative journalism, political research, transparency reporting, opposition research, government accountability. Deacon's use case (political ops, influence mapping) is squarely within permissible use.

**Data exposed:** Contributor name, home/business address, employer, occupation, exact donation amount, date. This is public record — FEC publishes it. No PII restrictions beyond the commercial solicitation prohibition.

---

## 2. Texas Ethics Commission (TEC) Data

### 2.1 What TEC Covers (vs. FEC)

FEC = **federal** races only (Congress, President).
TEC = **Texas state** races only (Governor, AG, Comptroller, RRC, State Legislature, statewide courts, local offices).

For Texas donor mapping, you need **both** — many big donors give at both levels.

### 2.2 TEC Bulk Data Access

**Main portal:** `https://www.ethics.state.tx.us`
**Bulk data page:** `https://www.ethics.state.tx.us/data/search/`
**Direct bulk downloads:** `https://www.ethics.state.tx.us/data/search/cf/` (campaign finance)

TEC provides bulk CSV files organized by filing type. Key files:

| File | Contents | URL Pattern |
|------|----------|-------------|
| `CONTRIBS_{YEAR}.csv` | Contributions to TX state candidates | `ethics.state.tx.us/data/search/cf/contribs_{year}.csv` |
| `EXPENDS_{YEAR}.csv` | Campaign expenditures by TX candidates | Same pattern, `expends_{year}.csv` |
| `NAMES_{YEAR}.csv` | Filer names + IDs (candidates, PACs) | `names_{year}.csv` |
| Lobby registrations | Registered lobbyists and clients | `ethics.state.tx.us/data/search/lobby/` |
| Lobby contributions | Lobbyist contributions to campaigns | Part of campaign finance bulk files |
| Personal financial statements | Officials' financial disclosures | PDFs only — not bulk accessible |

**Alternative access via TexasEthics.com:**
`https://www.texasethics.com` — third-party aggregator with cleaner UI and some export capability, but not full bulk access.

**File format:** CSV with header row, UTF-8. Filer IDs are TEC-assigned integers (not compatible with FEC IDs — join on name + address only).

**Update frequency:** TEC data updates after each filing deadline. TX campaign finance reporting periods:
- January 15 (year-end report, covering July–Dec prior year)
- July 15 (mid-year report, covering Jan–June)
- Pre-election reports (30-day and 8-day before each election)
- Semiannual reports for non-election years

**Data lag:** Typically 2–4 weeks after filing deadline before bulk files are updated.

### 2.3 TEC Key Fields (CONTRIBS table)

| Field | Description |
|-------|-------------|
| `filerIdent` | TEC filer ID (campaign/PAC) |
| `filerName` | Candidate or PAC name |
| `contributionDt` | Date of contribution |
| `amount` | Dollar amount |
| `contributorNameLast` | Donor last name |
| `contributorNameFirst` | Donor first name |
| `contributorStreetCity` | Donor city |
| `contributorStreetStateCode` | Donor state |
| `contributorStreetPostalCode` | Donor zip |
| `contributorEmployer` | Employer (if reported) |
| `contributorOccupation` | Occupation (if reported) |
| `reportInfoIdent` | Report ID (links to full filing) |

### 2.4 No TEC API

TEC does not offer a public API as of 2026. Access is bulk CSV only. Third-party wrappers:
- **Transparency USA** (`transparencyusa.org`) has indexed TEC data with a web interface — limited export
- **FollowTheMoney.org** has partial TX state data with API access

---

## 3. Cross-Referencing Approach

### 3.1 Core Logic

```
Individual Donor (name + address)
    │
    ├─── FEC Schedule A (federal giving)
    │        └─── TX federal candidates (Van Duyne, Self, Crockett, Veasey, Paxton)
    │
    └─── TEC CONTRIBS (state giving)
             └─── TX state candidates (Abbott, Paxton-AG era, state legislators)
    
    ↓ Joined on: donor_name + donor_city + donor_zip (fuzzy)
    
PAC/Committee Network
    ├─── FEC pas226 (PAC → candidate contributions)
    └─── TEC PAC data (TX-registered PAC → state candidate)
    
    ↓ Joined on: committee_name (fuzzy) + state

Influence Output
    ├─── Donor → Multiple candidates → Issue cluster
    ├─── Industry sector → District map
    └─── Lobbyist → Donor → Officeholder chain
```

### 3.2 Data Model / Schema

**SQLite database: `donors.db`**

```sql
-- Candidates table (source: FEC cn26 + TEC names)
CREATE TABLE candidates (
    id          TEXT PRIMARY KEY,   -- e.g. "FEC:H4TX24032" or "TEC:12345"
    source      TEXT,               -- 'FEC' or 'TEC'
    fec_id      TEXT,               -- FEC candidate ID (null for TEC-only)
    tec_id      TEXT,               -- TEC filer ID (null for FEC-only)
    name        TEXT NOT NULL,
    name_norm   TEXT,               -- normalized: uppercase, no punctuation
    office      TEXT,               -- 'H', 'S', 'P', 'GOV', 'AG', 'STATE_LEG'
    state       TEXT DEFAULT 'TX',
    district    TEXT,               -- e.g. '24' for TX-24
    party       TEXT,               -- 'REP', 'DEM', 'LIB'
    cycle       INTEGER,            -- 2026
    status      TEXT                -- 'ACTIVE', 'PRIOR'
);

-- Committees / PACs (source: FEC cm26 + TEC names)
CREATE TABLE committees (
    id          TEXT PRIMARY KEY,
    source      TEXT,
    fec_id      TEXT,
    tec_id      TEXT,
    name        TEXT NOT NULL,
    name_norm   TEXT,
    type        TEXT,               -- 'H','S','P','X','Y','Z','N','Q','O','U','V','W'
    designation TEXT,               -- 'P'=principal,'A'=authorized,'U'=unauthorized
    state       TEXT,
    city        TEXT,
    zip         TEXT,
    treasurer   TEXT
);

-- Candidate → Committee linkage
CREATE TABLE candidate_committee_link (
    candidate_id    TEXT REFERENCES candidates(id),
    committee_id    TEXT REFERENCES committees(id),
    cycle           INTEGER,
    is_principal    BOOLEAN
);

-- Individual contributions (source: FEC Schedule A + TEC CONTRIBS)
CREATE TABLE contributions (
    id                  TEXT PRIMARY KEY,   -- hash of source+fields
    source              TEXT NOT NULL,      -- 'FEC' or 'TEC'
    committee_id        TEXT REFERENCES committees(id),
    candidate_id        TEXT REFERENCES candidates(id),
    donor_id            TEXT REFERENCES donors(id),
    amount              REAL NOT NULL,
    contribution_date   DATE,
    receipt_type        TEXT,
    memo                TEXT,
    raw_donor_name      TEXT,               -- original as filed
    raw_employer        TEXT,
    raw_occupation      TEXT,
    cycle               INTEGER
);

-- Donors (deduplicated across FEC + TEC)
CREATE TABLE donors (
    id              TEXT PRIMARY KEY,   -- UUID assigned during dedup
    name_last       TEXT,
    name_first      TEXT,
    name_norm       TEXT,               -- uppercase, no punctuation, for matching
    address_street  TEXT,
    address_city    TEXT,
    address_state   TEXT,
    address_zip     TEXT,
    zip5            TEXT,               -- first 5 digits only
    employer        TEXT,
    occupation      TEXT,
    is_pac          BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP
);

-- Donor aliases (one donor may appear under multiple spellings)
CREATE TABLE donor_aliases (
    donor_id        TEXT REFERENCES donors(id),
    alias_name      TEXT NOT NULL,
    source          TEXT,
    match_method    TEXT    -- 'exact', 'fuzzy', 'manual'
);

-- PAC contributions (committee to committee, source: FEC pas226)
CREATE TABLE pac_contributions (
    id              TEXT PRIMARY KEY,
    source_committee_id TEXT REFERENCES committees(id),
    target_committee_id TEXT REFERENCES committees(id),
    amount          REAL,
    contribution_date DATE,
    cycle           INTEGER,
    memo            TEXT
);

-- Lobbyist registrations (source: TEC lobby data + Senate LD-1/LD-2)
CREATE TABLE lobbyists (
    id              TEXT PRIMARY KEY,
    source          TEXT,   -- 'TEC', 'SENATE_LDA'
    name            TEXT,
    employer        TEXT,   -- lobbying firm
    clients_json    TEXT,   -- JSON array of client names
    registration_year INTEGER,
    state           TEXT DEFAULT 'TX'
);

-- Lobbyist contributions (lobbyist → candidate, from TEC CONTRIBS joined on lobbyist registry)
CREATE TABLE lobbyist_contributions (
    contribution_id TEXT REFERENCES contributions(id),
    lobbyist_id     TEXT REFERENCES lobbyists(id),
    confidence      TEXT    -- 'HIGH' (exact match), 'MEDIUM' (fuzzy), 'LOW' (address only)
);
```

**Critical indexes for performance:**
```sql
CREATE INDEX idx_contributions_committee ON contributions(committee_id);
CREATE INDEX idx_contributions_cycle ON contributions(cycle);
CREATE INDEX idx_donors_zip5 ON donors(zip5);
CREATE INDEX idx_donors_name_norm ON donors(name_norm);
CREATE INDEX idx_contributions_source ON contributions(source);
```

### 3.3 Join Keys and Matching Strategy

**Within FEC (reliable):** `candidate_id`, `committee_id` — stable alphanumeric IDs, always reliable.

**FEC ↔ TEC (no shared ID — name matching required):**

| Match type | Reliability | Method |
|-----------|------------|--------|
| Exact name + exact zip | Very high | SQL `=` join on `name_norm + zip5` |
| Exact name + same city | High | SQL join on `name_norm + city_norm` |
| Fuzzy name + zip | Medium | Python `rapidfuzz` (threshold ≥ 0.88) |
| Employer match (no name) | Low | Use as supporting signal only |

**Name normalization function:**
```python
import re
def normalize_name(name):
    if not name: return ""
    name = name.upper()
    name = re.sub(r'[^A-Z0-9 ]', '', name)  # strip punctuation
    name = re.sub(r'\b(JR|SR|II|III|IV|ESQ|DR|MR|MRS|MS)\b', '', name)
    return " ".join(name.split())  # collapse whitespace
```

### 3.4 Investigation Query Patterns

**Pattern A — DFW Donor Map (Deacon's primary use case)**
```sql
-- All major donors in Plano/Allen/McKinney/Frisco/Irving zip codes
SELECT d.name_last, d.name_first, d.employer, d.address_city,
       SUM(c.amount) as total_given,
       GROUP_CONCAT(DISTINCT can.name) as candidates_supported
FROM donors d
JOIN contributions c ON c.donor_id = d.id
JOIN candidates can ON can.id = c.candidate_id
WHERE d.zip5 BETWEEN '75001' AND '75099'
   OR d.zip5 BETWEEN '75201' AND '75399'
   OR d.zip5 BETWEEN '76001' AND '76099'
GROUP BY d.id
HAVING total_given > 5000
ORDER BY total_given DESC;
```

**Pattern B — Paxton Senate Donor Network**
```sql
-- Everyone who gave to Ken Paxton's Senate committee
SELECT d.name_last, d.name_first, d.employer, d.address_city, d.address_state,
       c.amount, c.contribution_date
FROM contributions c
JOIN donors d ON d.id = c.donor_id
WHERE c.committee_id = 'C00901918'
  AND c.cycle = 2026
ORDER BY c.amount DESC;
```

**Pattern C — Bipartisan Donor (gives to both parties)**
```sql
SELECT d.id, d.name_last, d.name_first,
       SUM(CASE WHEN can.party = 'REP' THEN c.amount ELSE 0 END) as rep_total,
       SUM(CASE WHEN can.party = 'DEM' THEN c.amount ELSE 0 END) as dem_total
FROM donors d
JOIN contributions c ON c.donor_id = d.id
JOIN candidates can ON can.id = c.candidate_id
GROUP BY d.id
HAVING rep_total > 1000 AND dem_total > 1000
ORDER BY (rep_total + dem_total) DESC;
```

**Pattern D — Lobbyist → Officeholder Chain**
```sql
SELECT lb.name as lobbyist, lb.clients_json, lb.employer,
       can.name as candidate_supported, c.amount, c.contribution_date
FROM lobbyist_contributions lc
JOIN lobbyists lb ON lb.id = lc.lobbyist_id
JOIN contributions c ON c.id = lc.contribution_id
JOIN candidates can ON can.id = c.candidate_id
WHERE can.name LIKE '%VAN DUYNE%' OR can.name LIKE '%SELF%'
ORDER BY c.amount DESC;
```

---

## 4. Open-Source Tools and Libraries

### 4.1 What's Available

| Tool | Language | What It Does | Fit for This Project |
|------|----------|-------------|---------------------|
| **OpenPlanter** | Python | AI-driven FEC investigation agent — already in workspace at `research/openplanter-repo/` | ✅ Use for structured investigation runs |
| **python-fec** (`pip install fec`) | Python | Thin OpenFEC REST API wrapper with pagination helpers | ✅ Use for API pulls |
| **fec-loader** | Python | Loads FEC bulk ZIP files into PostgreSQL | ✅ Adapt for SQLite; handles field parsing |
| **pandas** | Python | CSV parsing and in-memory join operations | ✅ Already in workspace |
| **rapidfuzz** | Python | Fast fuzzy string matching (Levenshtein + token sort) | ✅ Required for name dedup |
| **sqlite3** | Python stdlib | Local database, zero infrastructure | ✅ MVP database |
| **Transparency USA** | Web (transparencyusa.org) | Pre-aggregated TEC + FEC data, TX-focused | ✅ Use for spot-checking and validation |
| **OpenSecrets API** | Web API | Well-structured FEC data, free tier 200 req/day | Optional — mainly useful for pre-built donor summaries |
| **FollowTheMoney.org API** | Web API | Multi-state campaign finance with TX TEC data | Optional — fills gaps in TEC bulk files |

### 4.2 What Does NOT Exist (Build Gap)

- **No tx-ethics-cli** — no command-line tool for TEC data exists publicly
- **No TEC API wrapper** — TEC has no public API, so no wrapper exists
- **No FEC ↔ TEC cross-ref engine** — the join layer described in Section 3 would be new
- **No DFW-specific donor map tool** — Bezzy would be building something novel here

### 4.3 OpenPlanter Notes (Existing Workspace Tooling)

OpenPlanter (`research/openplanter-repo/`) is an AI research agent that already knows FEC file formats. It successfully ran `texas-donors-run3` using `cn26.zip` and `cm26.zip`. Its limitation: no individual contribution data (`indiv26`) was present. Once `indiv26` data is loaded into the SQLite database, OpenPlanter can be re-run against it with a focused investigation prompt.

---

## 5. Implementation Plan

### 5.1 MVP (Low-Effort, ~5–6 hours Bezzy time)

**Goal:** A working SQLite database with TX individual contributions + TEC state contributions, queryable by donor name, zip code, and candidate. Produces CSV output.

**Steps:**

**Step 1 — FEC API Key (5 minutes)**
- Register at `https://api.data.gov/signup/`
- Store in `.env`: `FEC_API_KEY=your_key`

**Step 2 — FEC Data Pull (`scripts/fec_pull.py`, ~2 hours)**
- Query `/schedules/schedule_a/` with filters:
  - `contributor_state=TX`
  - `two_year_transaction_period=2026`
  - `per_page=100`
- Paginate all results (~500–1,000 pages expected)
- Save to `research/fec-data/fec-contributions-2026.csv`
- Also download `ccl26.zip` (candidate-committee linkage) for joining

**Step 3 — TEC Data Pull (`scripts/tec_pull.py`, ~30 minutes)**
- Download TEC bulk CSV from `https://www.ethics.state.tx.us/data/search/cf/contribs_2026.csv`
- Download `names_2026.csv` for filer name resolution
- Save to `research/tec-data/tec-contributions-2026.csv`

**Step 4 — Database Load (`scripts/load_db.py`, ~1 hour)**
- Create SQLite `research/donors.db` with schema from Section 3.2
- Load FEC CSV → `contributions` table (source='FEC')
- Load TEC CSV → `contributions` table (source='TEC')
- Load candidate/committee data from existing workspace files (`cn26.zip`, `cm26.zip`)
- Run name normalization on all donor records

**Step 5 — Donor Deduplication (`scripts/dedup_donors.py`, ~1 hour)**
- Group by `name_norm + zip5` (exact match first)
- Fuzzy match remaining with `rapidfuzz` threshold 0.88
- Assign `donor_id` UUIDs, populate `donors` and `donor_aliases` tables

**Step 6 — First Investigation Query (~30 minutes)**
- Run Pattern B (Paxton donor network) — output CSV
- Run Pattern A (DFW zip code map) — output CSV
- Save to `research/openplanter-runs/paxton-donors/` and `dfw-donor-map/`

**Deliverable:** A SQLite DB + 2 CSV reports. Bezzy runs, Berean interprets.

---

### 5.2 Nice-to-Have (Phase 2, ~1–2 days additional)

| Feature | Effort | Value |
|---------|--------|-------|
| Lobbyist integration (TEC lobby + Senate LD data) | ~3 hours | High — reveals lobbyist → officeholder chains |
| PAC-to-candidate flow (FEC pas226) | ~2 hours | Medium — maps industry PAC spending |
| Vote record integration (Congress.gov or GovTrack API) | ~4 hours | High — enables "donor gave to X, X voted Y" analysis |
| TX Legislature vote records (TLO — legis.texas.gov) | ~3 hours | High for state-level influence mapping |
| Web UI / dashboard | ~1 day | Low — nice for Deacon, not required for research |
| Automated weekly refresh cron | ~1 hour | Medium — keeps DB current through 2026 cycle |
| Name entity resolution (OpenAI API for ambiguous matches) | ~2 hours | Medium — improves dedup accuracy |
| Super PAC / 501(c)(4) tracker | ~1 day | High — dark money, hard to build |

---

### 5.3 Effort and Cost Summary

| Item | Estimate |
|------|---------|
| Bezzy build time (MVP) | ~5–6 hours |
| Bezzy build time (Phase 2, lobbyist + vote records) | ~10 hours additional |
| FEC data cost | $0 (public domain) |
| TEC data cost | $0 (Texas public records) |
| API keys | $0 (FEC) + $0 (TEC has no API) |
| Storage needed | ~2–4GB (FEC TX subset + TEC data) |
| Ongoing maintenance | ~1 hour/month to refresh data |

---

## 6. Key Risks and Limitations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Name matching false positives | Wrong donor → candidate linkages | Use address + zip as secondary confirmation; flag low-confidence matches |
| LLC/entity donations obscure individuals | Can't trace back to specific person | Note in findings; cross-reference business names with TX SOS records |
| Dark money (501c4) not in FEC | Major funding source invisible | Flag as known gap; use news sources + OpenSecrets for partial coverage |
| TEC filing delays (up to 4 months) | Stale data during active election season | Note data currency date on every report |
| FEC rate limits | Slow initial data pull | Use retry logic + exponential backoff; full TX pull takes ~30 min with key |
| API pagination volume | 500–1,000 pages for full TX Schedule A | Script pagination; expect 30–60 min runtime |

---

## 7. Recommended First Actions

1. **Bezzy: register FEC API key** — `api.data.gov/signup` — 5 minutes, unblocks everything
2. **Bezzy: write and run `fec_pull.py`** — TX Schedule A pull → CSV → SQLite
3. **Bezzy: download TEC 2026 bulk CSV** — `ethics.state.tx.us/data/search/cf/`
4. **Bezzy: load + dedup into `donors.db`**
5. **Berean: run Pattern B** (Paxton donor network) as first investigation
6. **Berean: run Pattern A** (DFW zip map) as second investigation

Vote records (Congress.gov) integration is Phase 2 — only add after MVP donor database is validated.

---

## Sources

- **FEC Bulk Data:** `https://www.fec.gov/data/browse-data/?tab=bulk-data`
- **OpenFEC API Docs:** `https://api.open.fec.gov/developers/`
- **FEC Data Dictionaries:** `https://www.fec.gov/campaign-finance-data/`
- **TEC Campaign Finance Search:** `https://www.ethics.state.tx.us/data/search/`
- **TEC Lobby Data:** `https://www.ethics.state.tx.us/data/search/lobby/`
- **Transparency USA (TX):** `https://www.transparencyusa.org/tx`
- **FollowTheMoney API:** `https://www.followthemoney.org/our-data/api/`
- **OpenSecrets API:** `https://www.opensecrets.org/api`
- **BL-006 Findings:** `research/openplanter-runs/texas-donors-run3/findings.md`
- **OpenPlanter FEC Wiki:** `research/openplanter-repo/wiki/campaign-finance/fec-federal.md`
- **Senate LDA Lobbying:** `research/openplanter-repo/wiki/lobbying/senate-ld.md`
