const express = require('express');
const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

const app = express();
const PORT = 3456;
const NOTES_DIR = path.join(__dirname, '..', 'notes');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Ensure notes directory exists
if (!fs.existsSync(NOTES_DIR)) fs.mkdirSync(NOTES_DIR, { recursive: true });

// --- Helpers ---

function slugify(text) {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '').substring(0, 60);
}

function noteFilename(title) {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, '0');
  const date = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`;
  const time = `${pad(now.getHours())}${pad(now.getMinutes())}`;
  return `${date}-${time}-${slugify(title || 'untitled')}.md`;
}

function readNote(filepath) {
  const raw = fs.readFileSync(filepath, 'utf8');
  const { data, content } = matter(raw);
  const id = path.basename(filepath, '.md');
  return { id, ...data, content: content.trim() };
}

function readAllNotes() {
  if (!fs.existsSync(NOTES_DIR)) return [];
  return fs.readdirSync(NOTES_DIR)
    .filter(f => f.endsWith('.md'))
    .map(f => {
      try { return readNote(path.join(NOTES_DIR, f)); }
      catch { return null; }
    })
    .filter(Boolean);
}

function writeNote(id, frontmatter, content) {
  const filepath = path.join(NOTES_DIR, `${id}.md`);
  const fm = { ...frontmatter };
  delete fm.id;
  delete fm.content;
  const raw = matter.stringify(content || '', fm);
  fs.writeFileSync(filepath, raw, 'utf8');
}

function extractTags(content) {
  const matches = content.match(/#([a-zA-Z0-9_-]+)/g);
  return matches ? [...new Set(matches.map(t => t.slice(1).toLowerCase()))] : [];
}

// --- API Routes ---

// List notes with optional filters
app.get('/api/notes', (req, res) => {
  let notes = readAllNotes();
  const { tag, category, search, archived, pinned } = req.query;

  // Default: hide archived
  if (archived !== 'true' && archived !== 'all') {
    notes = notes.filter(n => !n.archived);
  } else if (archived === 'true') {
    notes = notes.filter(n => n.archived);
  }

  if (tag) notes = notes.filter(n => n.tags && n.tags.includes(tag));
  if (category) notes = notes.filter(n => n.category === category);
  if (pinned === 'true') notes = notes.filter(n => n.pinned);
  if (search) {
    const q = search.toLowerCase();
    notes = notes.filter(n =>
      (n.title || '').toLowerCase().includes(q) ||
      (n.content || '').toLowerCase().includes(q) ||
      (n.tags || []).some(t => t.includes(q))
    );
  }

  // Sort: pinned first, then by modified desc
  notes.sort((a, b) => {
    if (a.pinned && !b.pinned) return -1;
    if (!a.pinned && b.pinned) return 1;
    return new Date(b.modified || b.created || 0) - new Date(a.modified || a.created || 0);
  });

  res.json(notes);
});

// Get single note
app.get('/api/notes/:id', (req, res) => {
  const filepath = path.join(NOTES_DIR, `${req.params.id}.md`);
  if (!fs.existsSync(filepath)) return res.status(404).json({ error: 'Not found' });
  res.json(readNote(filepath));
});

// Create note
app.post('/api/notes', (req, res) => {
  const { title, content, tags, category } = req.body;
  const now = new Date().toISOString();
  const autoTags = extractTags(content || '');
  const allTags = [...new Set([...(tags || []), ...autoTags])];
  const id = path.basename(noteFilename(title || content?.substring(0, 40) || 'untitled'), '.md');

  const frontmatter = {
    title: title || content?.substring(0, 60) || 'Untitled',
    tags: allTags,
    category: category || 'Random',
    pinned: false,
    archived: false,
    created: now,
    modified: now
  };

  writeNote(id, frontmatter, content || '');
  res.status(201).json({ id, ...frontmatter, content: content || '' });
});

// Update note
app.put('/api/notes/:id', (req, res) => {
  const filepath = path.join(NOTES_DIR, `${req.params.id}.md`);
  if (!fs.existsSync(filepath)) return res.status(404).json({ error: 'Not found' });

  const existing = readNote(filepath);
  const { title, content, tags, category, pinned, archived } = req.body;
  const now = new Date().toISOString();

  const updatedContent = content !== undefined ? content : existing.content;
  const autoTags = extractTags(updatedContent);
  const manualTags = tags !== undefined ? tags : (existing.tags || []);
  const allTags = [...new Set([...manualTags, ...autoTags])];

  const frontmatter = {
    title: title !== undefined ? title : existing.title,
    tags: allTags,
    category: category !== undefined ? category : existing.category,
    pinned: pinned !== undefined ? pinned : existing.pinned,
    archived: archived !== undefined ? archived : existing.archived,
    created: existing.created,
    modified: now
  };

  writeNote(req.params.id, frontmatter, updatedContent);
  res.json({ id: req.params.id, ...frontmatter, content: updatedContent });
});

// Archive note (soft delete)
app.delete('/api/notes/:id', (req, res) => {
  const filepath = path.join(NOTES_DIR, `${req.params.id}.md`);
  if (!fs.existsSync(filepath)) return res.status(404).json({ error: 'Not found' });

  const existing = readNote(filepath);
  const frontmatter = { ...existing, archived: true, modified: new Date().toISOString() };
  delete frontmatter.id;
  delete frontmatter.content;
  writeNote(req.params.id, frontmatter, existing.content);
  res.json({ success: true });
});

// Tags with counts
app.get('/api/tags', (req, res) => {
  const notes = readAllNotes().filter(n => !n.archived);
  const counts = {};
  notes.forEach(n => (n.tags || []).forEach(t => { counts[t] = (counts[t] || 0) + 1; }));
  res.json(Object.entries(counts).map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count));
});

// Categories with counts
app.get('/api/categories', (req, res) => {
  const notes = readAllNotes().filter(n => !n.archived);
  const counts = {};
  notes.forEach(n => { const c = n.category || 'Random'; counts[c] = (counts[c] || 0) + 1; });
  res.json(Object.entries(counts).map(([category, count]) => ({ category, count })).sort((a, b) => b.count - a.count));
});

app.listen(PORT, () => {
  console.log(`Notes app running at http://localhost:${PORT}`);
});
