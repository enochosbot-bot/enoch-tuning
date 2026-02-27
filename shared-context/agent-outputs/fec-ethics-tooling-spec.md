# FEC Donor Data + Texas Ethics Cross-Referencing Tooling — Spec
**Author:** Berean | **Date:** 2026-02-27 | **Task:** BL-012
**Status:** Research complete — ready for Bezzy build or Deacon approval

---

## 1. What FEC Bulk Data Downloads Are Available

### Primary Files (fec.gov/data/browse-data/?tab=bulk-data)
All files at `https://www.fec.gov/files/bulk-downloads/{year}/`:

| File | Contents | Size (2026) | Key For |
|------|----------|-------------|---------|
| `cn26.zip` | Candidate master (720KB) | ~720KB | Candidate → committee mapping |
| `cm26.zip` | Committee master | ~2.2MB | PAC/committee metadata |
| `indiv26.zip` | **Individual contributions** | ~4–6GB | Donor → candidate mapping |
| `pas226.zip` | PAC-to-candidate contributions | ~200MB | PAC spending by candidate |
| `oppexp26.zip` | Operating expenditures | ~500MB | Where campaigns spend |
| `ccl26.zip` | Candidate-committee linkage | small | Join key between candidates + committees |
| `weball26.zip` | All candidate financial summary | ~50MB | Top-line fundraising totals per candidate |

**Already in workspace:** `cn26.zip` (candidates), `cm26.zip` (committees), `tx-candidates-api.json` (557 TX candidates via FEC REST API).

**Critical missing file:** `indiv26.zip` — this is the individual contribution file. Without it, we cannot map donors to candidates by name or amount. It's ~4–6GB uncompressed; TX-only subset would be ~300–500MB.

### FEC REST API
- **Base URL:** `https://api.open.fec.gov/v1/`
- **Auth:** Free API key from `api.data.gov` (no cost, no approval — instant)
- **Key endpoints:**
  - `/schedules/schedule_a/` — individual contributions (filterable by state, candidate, date, amount)
  - `/schedules/schedule_b/` — disbursements
  - `/committees/` — committee search
  - `/candidates/` — candidate search
  - `/totals/` — summary financials
- **Rate limit:** 120 req/hr without key, 1000 req/hr with key
- **TX filter:** `contributor_state=TX` OR `candidate_office_state=TX`
- **Advantage over bulk:** no 6GB download; query what you need

**Recommended approach for initial build:** Use the REST API for targeted queries rather than bulk download. Bulk download is better for comprehensive offline analysis.

---

## 2. Texas Ethics Commission (TEC) — What Data Exists

The TEC covers **state-level** races only (Governor, AG, state legislature, local offices). This is separate from FEC federal data.

### TEC Data Available
**Website:** `ethics.state.tx.us`
**Search portal:** `ethics.state.tx.us/data/search/`

| Data Type | What It Contains | Access |
|-----------|-----------------|--------|
| Campaign finance reports | Contributions + expenditures for TX state candidates | Search + download per candidate |
| Lobby data | Registered lobbyists, their clients, spending | Bulk CSV available |
| Personal financial disclosures | State officials' financial interests | PDF per filer |
| PAC contributions | TX state PAC donors and amounts | Search + CSV |
| Vendor/contractor contributions | Business donors to state campaigns | Search |

**Bulk download:** TEC offers bulk CSV exports at `ethics.state.tx.us/dfs/oth_info.htm` and through their TexasEthics.com portal. Data is organized by filing year and entity type.

**Key tables for donor network analysis:**
- `CONTRIBS` — contributions to candidates (donor name, address, amount, date, candidate)
- `EXPENDS` — campaign expenditures (where money goes)
- `LOBBY_CLIENT` — lobbyists + their clients (who hires whom)
- `LOBBY_CONTRIBUTION` — lobbyist contributions to candidates

### TEC API
- No public API as of 2026. Data access is via bulk CSV export or web search.
- Third-party aggregators (Transparency USA, Open Secrets) have partially indexed TEC data.

---

## 3. Cross-Referencing Approach

### The Core Logic
The goal is: **donor name → multiple candidates → vote record or influence mapping**

```
Individual Donor
    ↓ (FEC indiv26 + TEC CONTRIBS)
Federal Candidates (FEC) + State Candidates (TEC)
    ↓ (committee linkage, PAC contributions)
PACs / Connected Organizations
    ↓ (FEC schedule A/B)
Vote records (Congress.gov, TLO for TX legislature)
    ↓
Influence map: "This donor gave to X candidates who all voted Y on Z issue"
```

### Specific Cross-Reference Patterns

**Pattern 1: Texas Donor Network Map**
- Pull all TX-address contributors from FEC `indiv26` (field: `contributor_state=TX`)
- Join on donor name + city to TEC `CONTRIBS`
- Result: donors who give at BOTH federal and state levels
- Use case: find the real players — donors who show up everywhere

**Pattern 2: Industry Cluster Analysis**
- Pull PAC contributions (FEC `pas226`) by industry code (FEC uses SIC-style codes)
- Match to TX candidates by district
- Cross-reference with TEC PAC contributions
- Result: which industries own which Texas districts

**Pattern 3: DFW Donor Network (Deacon's priority)**
- Filter FEC `indiv26` by `contributor_zip` in 750xx-751xx range (Plano, Allen, McKinney, Irving, Frisco, Dallas)
- Filter TEC `CONTRIBS` similarly
- Map to incumbents Van Duyne (24), Self (03), Williams (25), Crockett (30), Veasey (33)
- Result: who are the major donors in Deacon's backyard

**Pattern 4: Paxton Senate Race Donor Map (highest value)**
- Committee ID: `C00901918`
- Pull all Schedule A contributions via FEC API
- Cross-reference donor names with TEC to find state-level giving history
- Result: the Paxton donor network — who is funding the MAGA primary challenge to Cornyn

**Pattern 5: Lobbyist → Donor → Officeholder Chain**
- TEC `LOBBY_CLIENT` → lobbyist's clients
- TEC `LOBBY_CONTRIBUTION` → lobbyist gives to candidate
- FEC `indiv26` → same person also gives federally
- Result: the full picture of who influences a specific Texas politician

---

## 4. Open-Source Tools Already Built For This

| Tool | What It Does | Language | Status |
|------|-------------|----------|--------|
| **OpenFEC Python client** (`python-fec`) | Wraps FEC API with pagination | Python | Active, pip installable |
| **fec-loader** | Bulk loads FEC data into PostgreSQL | Python | GitHub, active |
| **FEC Scraper** (ProPublica) | Original FEC bulk data loader | Python | Older but well-documented |
| **OpenPlanter** | AI agent for FEC investigation (installed) | Python | In workspace at `/workspace/research/openplanter-repo/` |
| **Transparency USA** | Pre-aggregated TEC + FEC data, TX-focused | Web | `transparencyusa.org` — free search, limited bulk export |
| **FollowTheMoney.org** | Multi-state campaign finance aggregator | Web | Has TX data, API available |
| **OpenSecrets** | Federal FEC data, well-structured | Web | API available (free tier: 200 req/day) |
| **Pandas + SQLite** | Local analysis of bulk CSVs | Python | Already available in workspace |

**Best stack for local build:**
```
FEC REST API (schedule_a) → pandas → SQLite
TEC bulk CSV → pandas → same SQLite
SQLite cross-reference queries → findings output
```

---

## 5. Concrete Implementation Plan

### Phase 1 — Data Acquisition (Bezzy, ~2 hours)
1. Register free FEC API key at `api.data.gov` (instant)
2. Write `scripts/fec_pull.py`:
   - Pulls Schedule A contributions for TX candidates via FEC API
   - Filters by `candidate_office_state=TX`, `two_year_transaction_period=2026`
   - Saves to `research/fec-data/contributions-2026.csv`
3. Download TEC bulk contribution CSV from `ethics.state.tx.us`
4. Load both into `research/fec-data/donors.db` (SQLite)

### Phase 2 — Cross-Reference Engine (Bezzy, ~3 hours)
5. Write `scripts/donor_cross_ref.py`:
   - Input: candidate name or committee ID
   - Output: all donors + their other giving (federal + state)
   - Fuzzy name matching (donors don't always spell their names consistently)
6. DFW zip code filter function
7. Industry cluster aggregation from PAC data

### Phase 3 — Investigation Queries (Berean runs, ~1 hour)
8. Run Pattern 4 (Paxton donor network) as first investigation
9. Run Pattern 3 (DFW local donor map)
10. Save findings to `research/openplanter-runs/` with summary

### Estimated Effort
- Bezzy: ~5 hours total (Phases 1–2)
- Berean: ~1 hour per investigation run (Phase 3)
- Data storage: ~2GB for full FEC TX subset + TEC data

### Cost
- FEC data: **free** (public domain, no API cost)
- TEC data: **free** (Texas public records)
- OpenSecrets API: free tier (200 req/day) sufficient for spot checks
- Total: $0 operational cost

---

## 6. Limitations and Risks

1. **Name matching is hard** — "Robert Smith" and "Bob Smith" are the same person; requires fuzzy matching with address confirmation
2. **LLC/shell donations** — donors often give through business entities, obscuring the individual
3. **Dark money** — 501(c)(4) "social welfare" organizations don't file with FEC; their donors are invisible
4. **TEC filing delays** — campaigns file quarterly; data may be 3 months behind
5. **FEC indiv26 size** — 4–6GB uncompressed; TX-only via API is manageable but pagination-heavy
6. **No real-time data** — last FEC bulk update was 2026-02-19; API is ~48h behind

---

## Recommended First Action
**Bezzy should start with Phase 1** — register FEC API key and write the pull script. The DFW donor map (Pattern 3) and Paxton donor network (Pattern 4) are the two highest-value initial runs. Berean will execute Phase 3 once the database is built.

**Files to create:**
- `scripts/fec_pull.py` — FEC API data puller
- `scripts/donor_cross_ref.py` — cross-reference engine
- `research/fec-data/donors.db` — SQLite database
- `research/openplanter-runs/paxton-donors/` — first investigation output
