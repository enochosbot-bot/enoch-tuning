#!/usr/bin/env node
import fs from 'fs';
import path from 'path';

const ROOT = '/Users/deaconsopenclaw/.openclaw';
const backlogPath = path.join(ROOT, 'workspace/shared-context/backlog.md');
const inFlightPath = path.join(ROOT, 'workspace/ops/in-flight.md');
const agentsRoot = path.join(ROOT, 'agents');
const outPath = path.join(path.dirname(new URL(import.meta.url).pathname), 'data.js');

const AGENTS = [
  { name: 'Enoch', key: 'enoch', cls: 'Coordinator / Paladin', emoji: '🔮', sessionDir: 'main', color: '#8a6bff' },
  { name: 'Bezzy', key: 'bezzy', cls: 'Artificer / Builder', emoji: '⚙️', sessionDir: 'coder', color: '#34d399' },
  { name: 'Berean', key: 'berean', cls: 'Scholar / Ranger', emoji: '📚', sessionDir: 'researcher', color: '#60a5fa' },
  { name: 'Ezra', key: 'ezra', cls: 'Scribe / Bard', emoji: '✍️', sessionDir: 'scribe', color: '#f59e0b' },
  { name: 'Gideon', key: 'gideon', cls: 'Observer / Sentinel', emoji: '👁️', sessionDir: 'observer', color: '#22d3ee' },
  { name: 'Solomon', key: 'solomon', cls: 'Strategist / Sage', emoji: '🧠', sessionDir: 'solomon', color: '#f472b6' },
  { name: 'Selah', key: 'selah', cls: 'Artist / Druid', emoji: '🎨', sessionDir: 'creative', color: '#a78bfa' },
  { name: 'Nehemiah', key: 'nehemiah', cls: 'QA / Guardian', emoji: '🛡️', sessionDir: 'basher', color: '#fb7185' }
];

function safeRead(p) {
  try { return fs.readFileSync(p, 'utf8'); } catch { return ''; }
}

function parseBacklogCounts(md) {
  const counts = Object.fromEntries(AGENTS.map(a => [a.name, 0]));
  const regex = /^###\s+BL-\d+\s+\|[^|]*\|\s*(done|verified)\s*\|\s*([^\n|]+)/gim;
  for (const m of md.matchAll(regex)) {
    const ownerRaw = (m[2] || '').trim();
    const owner = ownerRaw.split('(')[0].trim();
    if (counts[owner] !== undefined) counts[owner] += 1;
  }
  return counts;
}

function parseInFlightLastActive(md) {
  const lastByAgent = Object.fromEntries(AGENTS.map(a => [a.name, null]));
  const lines = md.split('\n').filter(l => l.trim().startsWith('| BL-') || l.trim().startsWith('| RR-') || l.trim().startsWith('| Turn ') || l.trim().startsWith('| Wire ') || l.trim().startsWith('| Cron '));
  for (const line of lines) {
    const cols = line.split('|').map(s => s.trim());
    if (cols.length < 6) continue;
    const agentCol = cols[2] || '';
    const dispatched = cols[3] || '';
    const closed = cols[4] || '';
    const agentName = AGENTS.find(a => agentCol.toLowerCase().includes(a.name.toLowerCase()))?.name;
    if (!agentName) continue;
    const cand = [dispatched, closed].map(v => new Date(v)).filter(d => !Number.isNaN(d.valueOf())).sort((a,b)=>b-a)[0];
    if (!cand) continue;
    const prev = lastByAgent[agentName] ? new Date(lastByAgent[agentName]) : null;
    if (!prev || cand > prev) lastByAgent[agentName] = cand.toISOString();
  }
  return lastByAgent;
}

function parseSessionStats() {
  const now = Date.now();
  const cutoff = now - 24 * 60 * 60 * 1000;
  const out = Object.fromEntries(AGENTS.map(a => [a.name, { messages24h: 0, lastLogActivity: null }]));

  for (const agent of AGENTS) {
    const dir = path.join(agentsRoot, agent.sessionDir, 'sessions');
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter(f => f.endsWith('.jsonl'));
    for (const file of files) {
      const full = path.join(dir, file);
      const lines = safeRead(full).split('\n').filter(Boolean);
      for (const line of lines) {
        let row;
        try { row = JSON.parse(line); } catch { continue; }
        const ts = Date.parse(row.timestamp || row?.message?.timestamp || '');
        if (!Number.isFinite(ts)) continue;
        if (!out[agent.name].lastLogActivity || ts > Date.parse(out[agent.name].lastLogActivity)) {
          out[agent.name].lastLogActivity = new Date(ts).toISOString();
        }
        if (row.type === 'message' && row.message?.role === 'assistant' && ts >= cutoff) {
          out[agent.name].messages24h += 1;
        }
      }
    }
  }
  return out;
}

const backlog = safeRead(backlogPath);
const inFlight = safeRead(inFlightPath);
const completedCounts = parseBacklogCounts(backlog);
const inFlightLast = parseInFlightLastActive(inFlight);
const sessionStats = parseSessionStats();

const payload = {
  generatedAt: new Date().toISOString(),
  sources: { backlogPath, inFlightPath, agentsRoot },
  agents: AGENTS.map(a => ({
    name: a.name,
    className: a.cls,
    emoji: a.emoji,
    color: a.color,
    tasksCompleted: completedCounts[a.name] ?? 0,
    messages24h: sessionStats[a.name]?.messages24h ?? 0,
    lastActive: [sessionStats[a.name]?.lastLogActivity, inFlightLast[a.name]]
      .filter(Boolean)
      .sort((x, y) => Date.parse(y) - Date.parse(x))[0] || null
  }))
};

fs.writeFileSync(outPath, `window.DASHBOARD_DATA = ${JSON.stringify(payload, null, 2)};\n`);
console.log(`Wrote ${outPath}`);
