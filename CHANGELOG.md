# CHANGELOG

## v1.1 — February 19, 2026

### Added: Living Soul Protocol ⚠️ Significant behavioral change

This is the most important addition since v1.0.

Prior to this, SOUL.md was a static file. The agent read it, operated by it, and that was it. It couldn't propose changes to itself — which meant the only way it grew was if you manually edited the file yourself.

The Living Soul Protocol changes that.

Now the agent can notice patterns in how it actually operates, compare them against what SOUL.md says, and surface a formal proposal if they diverge. It doesn't rewrite itself — it asks first. You approve or reject. Only then does it write.

**Why this matters:**
- Agents that can't evolve get stale. The rules that made sense on day one don't always fit month three.
- Agents that evolve without accountability go rogue. Silent behavioral drift is worse than no evolution.
- The protocol threads that needle: growth with a human in the loop.

**What changed in the template:**
- Added `## Living Soul Protocol` section to `templates/SOUL.md`
- Defines the `🔮 SOUL PROPOSAL` format (section, current text, proposed text, why)
- Explicitly locks out changes to any file marked CONSTITUTION
- Agents propose → you approve → they write. No unilateral edits.

**If you installed v1.0:**
Add this section manually to your SOUL.md. It won't conflict with any personalization you've done — it goes at the bottom, before the closing line.

---

## v1.0 — February 19, 2026

Initial release.

- `SOUL.md` template — identity, decision heuristics, hard rules, anti-patterns, cost awareness
- `AGENTS.md` template — full operating protocol, verification, automation tiers, safety, idiot prevention
- `USER.md` template — user intake structure
- `MEMORY.md` template — long-term memory scaffold
- `MISSION.md` template — mission-driven idle behavior
- `ops/verification-protocol.md` — fact-checking protocol
- `setup/memory-structure.sh` — creates 8-category memory directory structure
- `setup/lock-identity.sh` — locks identity files to read-only
