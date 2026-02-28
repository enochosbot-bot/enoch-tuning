# Cron Registry
_Auto-exported. Source of truth: `ops/cron-definitions.json`. Re-import with `openclaw cron import` if gateway ever needs rebuild._

ID                                   Name                     Schedule                         Next       Last       Status    Target    Agent     
84b482b7-c7e7-4890-ac43-fe1746cac3df Shorty — Monitor for ... cron */5 * * * * @ America/Ch... in 1m      4m ago     ok        isolated  main
a4d836a9-ec46-4b08-acf1-ab816cae1173 Session Watchdog — Bl... cron 0 * * * * @ America/Chic... in 5m      55m ago    ok        isolated  observer
f66b156c-864a-4808-8cd7-13451ede9548 Session Auto-Prune       cron 0 */2 * * * @ America/Ch... in 1h      57m ago    ok        isolated  observer
2ec8c5a8-c257-444e-836d-87db90f5c941 Nightly Maintenance +... cron 0 3 * * * @ America/Chic... in 2h      22h ago    ok        isolated  main
920f1fe4-ad55-4813-aa89-1e5f3e73163c Gideon — Nightly Deep... cron 30 3 * * * @ America/Chi... in 3h      21h ago    ok        isolated  observer
79e87055-6119-49c0-aeef-7af5cfd61ce6 Gideon — Abaddon Nigh... cron 45 3 * * * @ America/Chi... in 3h      21h ago    ok        isolated  observer
7270d8de-cf06-4f12-b66e-548d4f9edff7 Berean — X Bookmarks ... cron 0 4 * * * @ America/Chic... in 3h      21h ago    error     isolated  researcher
50883b0d-e269-4b2c-b177-416e30067d0a Session Resume — Hand... cron 15 4 * * * @ America/Chi... in 3h      21h ago    error     isolated  main
cfe0e275-4c3e-43fd-9155-e42b9c6d301c qmd Reindex — Memory ... cron 30 */4 * * * @ America/C... in 4h      29m ago    ok        isolated  observer
dfb88b12-5b1e-412e-bd6b-66c58852c9c7 Gideon — Daily Quick ... cron 0 6 * * * @ America/Chic... in 5h      19h ago    ok        isolated  observer
37569b31-da87-496a-9ba4-fc8b28824499 Nehemiah — Daily Smok... cron 30 6 * * * @ America/Chi... in 6h      18h ago    ok        isolated  basher
454c0ba1-e104-42a9-a28c-0da09f840201 Backlog Intake — Task... cron 0 7 * * * @ America/Chic... in 6h      18h ago    ok        isolated  main
5235d2f8-e729-4a4e-8196-844b646d1df3 Morning Brief (8 AM)     cron 0 8 * * * @ America/Chic... in 7h      17h ago    ok        isolated  main
a74fc77c-6db4-4e17-b7cf-d0dd9cd3a1bb Daily Cost Report        cron 0 8 * * * @ America/Chic... in 7h      17h ago    ok        isolated  observer
df07756c-b4df-4a3f-997d-dbf62999f71f X Engagement Monitor ... cron 0 8 * * * @ America/Chic... in 7h      17h ago    ok        isolated  researcher
237f664f-eeb2-418d-be0a-396fe607a8ce Mission Pulse — Idle ... cron 0 9,12,15,18,21 * * * @ ... in 8h      4h ago     ok        isolated  main
df42afd5-fea7-4f4f-a848-5b0a10c76ffe Nehemiah — Output QA ... cron 0 10,16,22 * * * @ Ameri... in 9h      3h ago     ok        isolated  basher
bdef198a-ef84-43c4-b730-39ac6fb3c7d8 Weekly Memory Hygiene    cron 0 3 * * 0 @ America/Chic... in 1d      -          idle      isolated  main
46607546-34cd-4c0d-85a3-6300ed8f8aa1 Gideon — Weekly Full ... cron 0 8 * * 0 @ America/Chic... in 1d      5d ago     ok        isolated  observer
cc7456e9-c326-4ee9-aacb-ecf634671849 Stonebriar Brass Band... at 2026-03-15 01:00Z             in 15d     -          idle      main      main
f8484f6f-2683-4ebc-abcd-b6fe9820c87c Reminder: Start looki... at 2026-04-01 16:00Z             in 32d     -          idle      main      main
