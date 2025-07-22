# 🛣️ Coddy V3 Roadmap

Coddy is being built to support the creative-coding flow: design your ideas, chat them into roadmaps, then code alongside AI in the same dashboard.

---

## ✅ MVP Milestones

### Phase 1: 🔁 Project Initialization

- [x] Create Landing Page with Load/Create Project
  - [x] Sub-task: Implement window creation and main loop management in `app.py`.
  - [x] Sub-task: Design and implement the Tkinter-based landing page UI (`landing_page.py`), including welcome text, taglines, and action buttons.
- [x] Task: Implement Python's `os` module for local file system access
  - [x] Sub-task: Integrate file dialogs for project folder selection (e.g., `filedialog.askdirectory`).
  - [x] Sub-task: Implement creation of new project directories within `coddy_codes/` (`os.makedirs`).
  - [x] Sub-task: Develop functions for reading and listing directory contents (`os.listdir`, `os.path.join`, `os.path.isfile`, `os.path.isdir`).
- [x] Task: Implement local project metadata storage via `config_manager` (settings.json and .env)
  - [ ] Sub-task: Develop functions for loading and saving application-wide settings (e.g., last active theme, `unorthodox_ideas` slider value) in `settings.json`.
  - [x] Sub-task: Implement secure storage and retrieval of AI API keys (e.g., `GEMINI_API_KEY`) in the `.env` file.

---

### Phase 2: 🌱 Genesis Tab

- [ ] Task: Build Genesis chat interface using Tkinter
  - [ ] Sub-task: Design the chat history display using `tk.Text` widget with scrolling.
  - [ ] Sub-task: Implement user input handling using `tk.Entry` and a 'Send' button.
  - [ ] Sub-task: Integrate 'Weird Idea', 'Generate README', and 'Generate Roadmap' buttons.
- [ ] LLM API call to turn chat → README
  - [ ] Sub-task: Configure `AIEngine` with `google.generativeai` and the Gemini model.
  - [ ] Sub-task: Implement initial system prompts for project definition and README generation.
  - [ ] Sub-task: Develop threading for AI calls to prevent UI freezing.
- [ ] Generate roadmap from README
  - [ ] Sub-task: Define specific system prompts and markdown structure for roadmap generation.
- [ ] Display phases + tasks visually
  - [ ] Sub-task: Ensure generated `roadmap.md` adheres to a structured, phase-based markdown format.
- [ ] Save roadmap to project context
  - [ ] Sub-task: Implement `save_roadmap` function in `main_application` to write markdown content to `roadmap.md` within the project folder.
- [ ] Add “💡 Give Me an Idea” button
  - [ ] Normal mode → standard startup/app ideas
  - [ ] Weird mode → wild & absurd ideas only
  - [ ] Sub-task: Implement button action to send a predefined "weird idea" prompt to the AI.

---

### Phase 3: 🎨 Theme System

- [ ] Task: Implement theme application logic across Tkinter widgets
  - [ ] Sub-task: Develop a centralized theme module (`theme.py`) defining color palettes (background, foreground, accent, etc.).
  - [ ] Sub-task: Implement methods in `MainApplication`, `LandingPage`, and individual tabs to apply selected theme colors to all relevant UI elements.
- [ ] Task: Store selected theme in application configuration via `config_manager`
  - [ ] Sub-task: Integrate theme selection persistence using `config_manager.save_config`.
- [ ] Task: Define Light, Dark, and Weird color palettes in `theme.py` for Tkinter styling
  - [ ] Sub-task: Define distinct color dictionaries for 'dark', 'light', and 'weird' themes.
- [ ] Task: Implement theme toggle buttons on the Landing Page and Main Application
  - [ ] Sub-task: Create interactive buttons to switch themes (`LandingPage.switch_theme`, `MainApplication.switch_theme`).

---

### Phase 4: ✍️ Edit Tab

- [ ] View + edit file contents
  - [ ] Sub-task: Implement `ttk.Treeview` for displaying the project's file structure.
  - [ ] Sub-task: Develop file selection handler to load content into a `tk.Text` widget for viewing/editing.
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

- [ ] Task: Implement saving of Gemini API key via `config_manager` into .env file
  - [ ] Sub-task: Create an `Entry` widget for Gemini API key input.
  - [ ] Sub-task: Implement focus-in/focus-out handlers for placeholder text and password masking.
  - [ ] Sub-task: Link API key entry to `config_manager.save_gemini_key`.
- [ ] Theme switcher
- [ ] Task: Implement 'Unorthodox Ideas' slider for AI behavior adjustment
  - [ ] Sub-task: Integrate a `ttk.Scale` widget for adjusting AI's 'unorthodox ideas' parameter (0-100).
  - [ ] Sub-task: Persist slider value using `config_manager`.
- [ ] Developer preferences (autosave, debug info)

---

## 💸 Subscription Tier Logic

Tier logic is designed to control feature access based on subscription level.

All users can:

- See all tabs and tools
- Get limited functionality based on tier
- Access Weird Mode and idea generator

---

## 🌟 Current Focus: Phase 1–3

- Landing Page, Genesis Chat, Theme Toggle
