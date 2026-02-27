# OpenNotes — Product Spec v1

**Platform:** iOS (Swift / SwiftUI)
**Reference:** MinimaList
**Goal:** A dead-simple task list app. Minimal friction, maximum speed. Just tasks.

---

## Core Interaction Model

### Task List (Main View)
- Flat vertical list of tasks, plain text, generous line spacing
- New tasks added to the top (or bottom — TBD)
- No visible UI chrome beyond the task text — clean white background, black text
- Completed tasks: gray text + strikethrough, sink to bottom of list

### Gestures

| Gesture | Action |
|---------|--------|
| **Swipe left→right** | Progressive strikethrough drawn at swipe pace. Full swipe = task completed. Haptic feedback on completion. Task animates down to bottom of list (gray + strikethrough). |
| **Swipe left→right on completed task** | Un-crosses it. Restores to active list. |
| **Swipe right→left** | Opens side action panel (edit/delete icons slide in from right) |
| **Tap task** | Expands task inline with options panel |
| **Swipe up** | Clean view — hides completed items, shows active only |
| **Swipe down** (from top of list) | Opens blank full-screen editor to add new task |
| **Pinch** | Opens multi-list manager (low priority — nice to have) |

### Expanded Task (Tap to Open)
When tapped, task expands inline showing:
- **Add note** — text field for extra details
- **Add subtask** — checkbox-style sub-items
- **Bottom toolbar:**
  - 🗑 Delete
  - ✏️ Edit
  - 🍅 Focus Time (timer)
  - ✅ Done (cross off)

### Delete Flow
- Tap trash icon → confirmation modal: "Are you sure you want to remove the task?"
- Cancel / **Confirm** buttons
- Confirm → task removed with closing animation

---

## Completed Archive View
- Accessible from main view (swipe or button — TBD)
- **Search bar** at top
- **Filter dropdown** ("All" + other filters TBD)
- **Settings gear** icon
- Tasks grouped by **date completed** with timestamps
- **Bottom stats bar:** total completed count + total focused time
- **"More >"** link for pagination/extended history

---

## Data Model

```
Task {
  id: UUID
  text: String
  note: String?
  isCompleted: Bool
  completedAt: Date?
  createdAt: Date
  subtasks: [Subtask]
  focusedSeconds: Int
}

Subtask {
  id: UUID
  text: String
  isCompleted: Bool
}
```

---

## Design Principles
1. **Speed over features** — adding a task should be < 2 seconds
2. **Tactile feedback** — haptics on cross-off, smooth animations everywhere
3. **No cognitive load** — no categories, tags, priorities, or colors. Just text.
4. **Progressive disclosure** — task options hidden until you tap
5. **Forgiving** — cross-off is reversible, delete requires confirmation

---

## Task Editor (Full Screen)
Triggered by: tap task → tap Edit, or swipe down (TBD confirm)
- Task text at top (editable, cursor active)
- **Add note** — text field below task
- **Add subtask** — below note
- Keyboard appears with **blue checkmark** button (save/confirm)
- **Toolbar above keyboard** (icon row):
  - 🔔 Reminder/notification
  - ⭐ Star/favorite
  - 🔁 Repeat
  - 🍅 Focus
  - 🔔 Notification bell
  - (exact icons TBD — need to confirm each function)

## Focus Time
- Simple stopwatch/timer — NOT Pomodoro
- Full red screen with large timer display (HH:MM:SS)
- Single "Stop Recording" button
- Tracks focused seconds per task

## Open Questions
- [x] Dark mode — YES, required. Ship with both light + dark.
- [ ] iCloud sync — post-launch if there's demand
- [ ] Widget support?
- [ ] Data export/import from MinimaList?
- [x] Swipe down from top of list = add new task ✅
- [ ] What do each of the toolbar icons above keyboard do exactly?
- [ ] Star/favorite — does it pin tasks to top?
- [ ] Repeat — recurring tasks?

---

## Tech Stack
- **Language:** Swift
- **UI:** SwiftUI
- **Storage:** SwiftData (or Core Data) — local first
- **Min iOS:** 17.0
- **Architecture:** MVVM

---

*Spec v1 — Feb 15, 2026*
