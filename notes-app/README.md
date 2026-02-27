# Notes App

Personal notes app with markdown support, tagging, and OpenClaw integration.

## Quick Start
```bash
cd ~/.openclaw/workspace/notes-app
npm install
node server.js
```
Open http://localhost:3456

## Features
- Quick capture bar (type + Enter)
- Markdown editing with preview toggle
- Auto-extracted #tags from content
- Categories: Ideas, Tasks, People, Research, Random
- Pin/star and archive notes
- Full-text search
- Keyboard shortcuts: ⌘N (new), ⌘K (search), ⌘Enter (save)
- Mobile responsive

## API
- `GET /api/notes` — list (filters: `?tag=x&category=x&search=x&archived=true&pinned=true`)
- `GET /api/notes/:id` — single note
- `POST /api/notes` — create `{title, content, tags[], category}`
- `PUT /api/notes/:id` — update
- `DELETE /api/notes/:id` — archive
- `GET /api/tags` — tag counts
- `GET /api/categories` — category counts

## Storage
Notes are markdown files with YAML frontmatter in `~/.openclaw/workspace/notes/`
