# 🛣️ `roadmap.md` (Complete Version)

```markdown
# 🛣️ Coddy V3 Roadmap

Coddy is being built to support the creative-coding flow: design your ideas, chat them into roadmaps, then code alongside AI in the same dashboard.

---

## ✅ MVP Milestones

### Phase 1: 🔁 Project Initialization
- [ ] Create Landing Page with Load/Create Project
- [ ] File access layer (Node / Tauri / Electron)
- [ ] Project metadata state (stored in backend or browser)

---

### Phase 2: 🌱 Genesis Tab
- [ ] Build Genesis chat interface (React)
- [ ] LLM API call to turn chat → README
- [ ] Generate roadmap from README
- [ ] Display phases + tasks visually
- [ ] Save roadmap to project context
- [ ] Add “💡 Give Me an Idea” button
  - [ ] Normal mode → standard startup/app ideas
  - [ ] Weird mode → wild & absurd ideas only

---

### Phase 3: 🎨 Theme System
- [ ] Add `ThemeProvider` context
- [ ] Store theme in localStorage
- [ ] Create Light, Dark, and Weird CSS modes
- [ ] Add 3 toggle buttons (bottom-left dashboard)

---

### Phase 4: ✍️ Edit Tab
- [ ] View + edit file contents
- [ ] Send code + task to LLM → receive suggestion
- [ ] Apply AI edit inline (Creator+ tier)
- [ ] Full semantic refactor (Architect+)

---

### Phase 5: ✅ Tasks Tab
- [ ] Visual roadmap viewer (cards, lists)
- [ ] Track completed tasks
- [ ] AI summaries of sessions
- [ ] Auto-task planning (Visionary tier)

---

### Phase 6: 👤 Auth + Tiers
- [ ] Login / Signup with Firebase or JWT
- [ ] Load user profile + active tier
- [ ] Lock or limit features based on tier
- [ ] Show “Upgrade” prompt on locked tools

---

### Phase 7: ⚙️ Settings Tab
- [ ] Save LLM keys (OpenAI, Claude, etc.)
- [ ] Theme switcher
- [ ] AI personality toggle (Visionary+)
- [ ] Developer preferences (autosave, debug info)

---

## 💸 Subscription Tier Logic

Tier logic stored in:
- `shared/constants/subscription_tiers.json`
- Enforced by:
  - `useSubscriptionTier()` hook in frontend
  - FastAPI middleware on backend

All users can:
- See all tabs and tools
- Get limited functionality based on tier
- Access Weird Mode and idea generator

---

## 🌟 Current Focus: Phase 1–3
- Landing Page, Genesis Chat, Theme Toggle
