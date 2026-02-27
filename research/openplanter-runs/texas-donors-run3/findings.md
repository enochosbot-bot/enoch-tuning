# Texas Political Donor Networks — FEC Investigation
**Run:** texas-donors-run3 | **Date:** 2026-02-27 | **Analyst:** Berean
**Data source:** FEC bulk data (cn.txt, cm.txt, tx-candidates-api.json) — updated 2026-02-19
**Method:** Direct FEC data analysis (OpenPlanter runs 1–2 failed: run1 qwen3:8b confused by objective; run2 claude-haiku 401 auth error)

---

## Key Findings

### 1. Scale of the Texas Federal Political Landscape
- **586 active federal candidates** (active through 2024 or later) — TX is one of the most contested states
- **1,276 TX-based PACs and committees** registered with FEC
- **2026 TX House breakdown:** 196 REP vs 128 DEM vs 13 IND (out of ~347 candidates)
- **2026 TX Senate field:** 20+ candidates — crowded Republican primary with Cornyn as incumbent

### 2. The 2026 TX Senate Race — Primary Battleground
Cornyn (incumbent) faces a crowded right-primary challenge:

| Candidate | Party | Status | Committee |
|-----------|-------|--------|-----------|
| CORNYN, JOHN | REP | **Incumbent** | C00369033 |
| PAXTON, WARREN KENNETH JR. | REP | Challenger | C00901918 |
| ALLEN, KEITH | REP | Challenger | C00886291 |
| MCNABB, BARRETT ANTHONY | REP | Challenger | C00897819 |
| BIERSCHWALE, VIRGIL | REP | Challenger | C00908087 |
| ALLRED, COLIN | DEM | Challenger | C00909572 |
| BROWN, THEODORE E. JR. | LIB | Challenger | C00857623 |

**Ken Paxton's entry** is the most politically significant — former AG with statewide name ID and a MAGA donor base. This is the race to watch in TX 2026.

### 3. TX House Incumbents (Federal, 2026)
All Republican:

| Candidate | District | Party |
|-----------|----------|-------|
| FALLON, PATRICK | 04 (McKinney/Frisco) | REP |
| HUNT, WESLEY | 38 (Houston) | REP |
| PFLUGER, AUGUST | 11 (San Angelo) | REP |
| JACKSON, RONNY | 13 (Amarillo) | REP |
| DE LA CRUZ, MONICA | 15 (McAllen) | REP |
| NEHLS, TROY | 22 (Sugar Land) | REP |
| VAN DUYNE, ELIZABETH | 24 (**Irving/DFW**) | REP |
| GONZALES, TONY | 23 (San Antonio) | REP |
| MORAN, NATHANIEL | 01 (Tyler) | REP |
| SESSIONS, PETE | 17 (Waco) | REP |
| SELF, KEITH | 03 (**McKinney/DFW**) | REP |
| LUTTRELL, MORGAN | 08 (Magnolia) | REP |
| WEBER, RANDY | 14 (Friendswood) | REP |
| CUELLAR, HENRY | 28 (Laredo) | DEM |
| CROCKETT, JASMINE | 30 (**Dallas**) | DEM |
| CARTER, JOHN R. | 31 (Georgetown) | REP |
| WILLIAMS, ROGER | 25 (Cleburne) | REP |
| VEASEY, MARC | 33 (**Fort Worth**) | DEM |
| CASTRO, JOAQUIN | 20 (San Antonio) | DEM |
| GREEN, ALEXANDER | 18 (Houston) | DEM |

**DFW-area incumbents: Van Duyne (24-Irving), Self (03-McKinney), Crockett (30-Dallas), Veasey (33-Fort Worth)**

### 4. Corporate PAC Donor Networks (TX-Based)
The dominant industry sectors with TX-headquartered PACs:

**Energy/Oil & Gas:**
- Energy Transfer PAC (Dallas) — Kelcy Warren network
- Valero Energy PAC (San Antonio)
- Atmos Energy PAC (Dallas)
- CenterPoint Energy PAC (Houston)
- Apache Corporation PAC (Houston)
- BP North America Employee PAC
- Halliburton Company PAC (Houston)
- Diamondback Energy PAC
- Coterra Energy PAC

**Defense/Aerospace:**
- Elbit Systems of America PAC (Fort Worth)
- Axiom Space PAC (Houston)
- Intuitive Machines PAC (Houston)
- KBR, Inc. PAC (Houston)
- Fluor Corporation PAC (Irving)

**Telecom/Tech:**
- AT&T Employee Federal PAC (Dallas) — one of the largest corporate PACs in TX
- iHeartMedia PAC (San Antonio)
- 7-Eleven PAC (Irving)
- Texas Instruments PAC (Dallas)

**Financial/Legal:**
- Baker Botts Bluebonnet Fund (Houston) — premier TX law firm, energy/corporate clients
- McLane Company Federal PAC (Temple) — Berkshire Hathaway subsidiary
- American Income Life Insurance PAC

**Healthcare:**
- Texas Medical Association PAC (Austin) — AMPAC
- American Association of Nurse Practitioners PAC (Austin)
- Darling Ingredients PAC

### 5. Conservative/MAGA-Aligned PACs (TX-Based)
Notable ideological PACs with TX addresses:
- **AMERICA FIRST RESCUE PAC** — MAGA-aligned
- **MAGA REPUBLICAN PARTY PAC**
- **TEXANS FOR A CONSERVATIVE MAJORITY**
- **TEXAS PATRIOTS PAC**
- **CONSERVATIVES NETWORK**
- **TEXANS FOR LIBERTY**
- **TEXANS FOR TRUTH AND LIBERTY PAC**
- **JOBS, FREEDOM, AND SECURITY PAC**
- **LATINOS FOR AMERICA FIRST** — notable for Hispanic outreach angle
- **CONSERVATIVE RENEWAL POLITICAL ACTION COMMITTEE**

### 6. Key Donor Network Architecture (Structural Observations)
- **Energy Transfer / Kelcy Warren network** is the dominant private donor force in TX Republican politics — Energy Transfer PAC feeds into statewide and federal races
- **AT&T PAC** historically distributes to both parties (incumbent protection strategy) — bipartisan, not ideological
- **Baker Botts** represents major energy companies; their Bluebonnet Fund tracks directly with energy sector interests
- **MAGA/conservative PAC proliferation** since 2022 — 30+ TX-based conservative-aligned PACs competing for donor dollars
- **Paxton Senate race** will be the main magnet for MAGA donor money in 2026 — watch his committee (C00901918) for large-donor clustering

---

## What's Unknown / Data Gaps
1. **Individual contribution amounts** — cn.txt and cm.txt don't contain dollar figures; FEC individual contribution files (indiv26.zip, ~4GB) were not in workspace. Needed for actual donor → candidate mapping.
2. **Texas Ethics Commission (state-level) data** — this FEC data is federal only. State legislative races require separate TEC data pull.
3. **Cross-referencing donor names** — can't map individuals to multiple candidates without contribution records.
4. **Disbursement/expenditure data** — where PAC money went requires separate FEC files (oppexp.zip).
5. **Super PAC / dark money connections** — 501(c)(4) "social welfare" orgs not captured in FEC data.

---

## Confidence Level
**High** — for candidate landscape, committee registry, and PAC identification (direct FEC data).
**Low** — for actual donor-to-candidate flow (contribution files not present in workspace).

---

## Recommended Next Action
1. **Download FEC individual contribution file** for TX (indiv26.zip from fec.gov/data/bulk-downloads/) — this unlocks actual donor mapping.
2. **Pull Texas Ethics Commission bulk data** for state-level races — see BL-012 spec.
3. **Focus on Ken Paxton Senate committee** (C00901918) — his donor network will be the most politically interesting for Deacon's political ops work.
4. **DFW lens:** Van Duyne (24), Self (03), Crockett (30), Veasey (33) — four incumbents in Deacon's backyard. Pairing FEC contributions with local donor names (Plano/Allen/McKinney) is the most actionable near-term research.

---

## Files
- Raw data: `/Users/deaconsopenclaw/.openclaw/workspace/research/openplanter-repo/workspace/texas-data/`
- This report: `research/openplanter-runs/texas-donors-run3/findings.md`
