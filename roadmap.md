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
  - [x] Sub-task: Develop functions for loading and saving application-wide settings (e.g., last active theme, `unorthodox_ideas` slider value) in `settings.json`.
  - [x] Sub-task: Implement secure storage and retrieval of AI API keys (e.g., `GEMINI_API_KEY`) in the `.env` file.

---

### Phase 2: 🌱 Genesis Tab

- [x] Task: Build Genesis chat interface using Tkinter
  - [x] Sub-task: Design the chat history display using `tk.Text` widget with scrolling.
  - [x] Sub-task: Implement user input handling using `tk.Entry` and a 'Send' button.
  - [x] Sub-task: Integrate 'Weird Idea', 'Generate README', and 'Generate Roadmap' buttons.
- [x] LLM API call to turn chat → README
  - [x] Sub-task: Configure `AIEngine` with `google.generativeai` and the Gemini model.
  - [x] Sub-task: Implement initial system prompts for project definition and README generation.
  - [x] Sub-task: Develop threading for AI calls to prevent UI freezing.
- [x] Generate roadmap from README
  - [x] Sub-task: Define specific system prompts and markdown structure for roadmap generation.
- [x] Display phases + tasks visually
  - [x] Sub-task: Ensure generated `roadmap.md` adheres to a structured, phase-based markdown format.
- [x] Save roadmap to project context
  - [x] Sub-task: Implement `save_roadmap` function in `main_application` to write markdown content to `roadmap.md` within the project folder.
- [x] Add “💡 Give Me an Idea” button
  - [x] Normal mode → standard startup/app ideas
  - [x] Weird mode → wild & absurd ideas only
  - [x] Sub-task: Implement button action to send a predefined "weird idea" prompt to the AI.

---

### Phase 3: 🎨 Theme System

- [x] Task: Implement theme application logic across Tkinter widgets
  - [x] Sub-task: Develop a centralized theme module (`theme.py`) defining color palettes (background, foreground, accent, etc.).
  - [x] Sub-task: Implement methods in `MainApplication`, `LandingPage`, and individual tabs to apply selected theme colors to all relevant UI elements.
- [x] Task: Store selected theme in application configuration via `config_manager`
  - [x] Sub-task: Integrate theme selection persistence using `config_manager.save_config`.
- [x] Task: Define Light, Dark, and Weird color palettes in `theme.py` for Tkinter styling
  - [x] Sub-task: Define distinct color dictionaries for 'dark', 'light', and 'weird' themes.
- [x] Task: Implement theme toggle buttons on the Landing Page and Main Application
  - [x] Sub-task: Create interactive buttons to switch themes (`LandingPage.switch_theme`, `MainApplication.switch_theme`).

---

### Phase 4: ✍️ Edit Tab

- [x] View + edit file contents
  - [x] Sub-task: Implement `ttk.Treeview` for displaying the project's file structure.
  - [x] Sub-task: Develop file selection handler to load content into a `tk.Text` widget for viewing/editing.
- [x] Send code + task to LLM → receive suggestion
  - [x] Sub-task: Add UI elements (input field, button) to the Edit Tab for AI interaction.
  - [x] Sub-task: Implement a handler to send the current code and user task to the AI engine in a thread.
  - [x] Sub-task: Create a new window to display the AI's suggestion.
- [x] Apply AI edit inline (Creator+ tier)
  - [x] Sub-task: Upgrade suggestion window to be interactive with "Apply" and "Cancel" buttons.
  - [x] Sub-task: Implement logic to replace selected text or the whole file with the AI suggestion.
  - [x] Sub-task: Add tier check for the "Apply" functionality.
  - [x] Sub-task: Refine AI prompt to return only raw code for easier application.
- [x] Full semantic refactor (Architect+)
  - [x] Sub-task: Add "Full Refactor" button to the Edit Tab.
  - [x] Sub-task: Implement a new AI engine method with a specialized prompt for deep refactoring.
  - [x] Sub-task: Gate the feature to the "Architect" tier.

---

### Phase 5: ✅ Tasks Tab

- [x] Visual roadmap viewer (cards, lists)
  - [x] Sub-task: Create `TasksTab` module to display roadmap content.
  - [x] Sub-task: Implement a parser for `roadmap.md` to extract phases and tasks.
  - [x] Sub-task: Render phases and tasks using Tkinter widgets in a scrollable view.
- [x] Track completed tasks
  - [x] Sub-task: Enable checkboxes and bind them to a save function.
  - [x] Sub-task: Implement logic to rewrite `roadmap.md` with updated task statuses.
- [x] AI summaries of sessions
  - [x] Sub-task: Add "Summarize Session" button to the Tasks Tab.
  - [x] Sub-task: Create a new AI engine method for generating summaries from roadmap content.
  - [x] Sub-task: Gate the feature to the "Architect" tier.
- [x] Auto-task planning (Visionary tier)
  - [x] Sub-task: Add "Visionary" tier and `AUTO_TASK_PLANNING` feature to `subscription.py`.
  - [x] Sub-task: Add "Auto-plan" button to the Tasks Tab with a confirmation dialog.
  - [x] Sub-task: Create a new AI engine method for generating a full roadmap from a high-level goal.
  - [x] Sub-task: Implement logic to overwrite `roadmap.md` and refresh the UI.

---

### Phase 6: 👤 Auth + Tiers

- [x] Login / Signup with Firebase or JWT
  - [x] Sub-task: Create `auth.py` with a simulated user database for local testing.
  - [x] Sub-task: Create a modal `LoginWindow` UI for login and signup forms.
- [x] Load user profile + active tier
  - [x] Sub-task: Implement session management (`current_user`) in `MainApplication`.
  - [x] Sub-task: Add login/logout controls and user status display to the Settings tab.
  - [x] Sub-task: Update the application's active tier based on the logged-in user's profile.
- [x] Task: Implement local subscription tier simulation for testing
  - [x] Sub-task: Create `subscription.py` to define tiers and feature access.
  - [x] Sub-task: Add a tier selector dropdown to the Settings tab.
  - [x] Sub-task: Load and save the selected tier via `config_manager`.
  - [x] Sub-task: Implement feature-locking logic in `EditTab` to restrict AI suggestions.

---

### Phase 7: ⚙️ Settings Tab

- [x] Task: Implement saving of Gemini API key via `config_manager` into .env file
  - [x] Sub-task: Create an `Entry` widget for Gemini API key input.
  - [x] Sub-task: Implement focus-in/focus-out handlers for placeholder text and password masking.
  - [x] Sub-task: Link API key entry to `config_manager.save_gemini_key` via `MainApplication.save_settings`.
- [x] Theme switcher
  - [x] Sub-task: Add a theme selection combobox to the Settings tab.
  - [x] Sub-task: Implement logic to apply and persist the selected theme immediately.
- [x] Task: Implement 'Unorthodox Ideas' slider for AI behavior adjustment
  - [x] Sub-task: Integrate a `ttk.Scale` widget for adjusting AI's 'unorthodox ideas' parameter (0-100).
  - [x] Sub-task: Persist slider value using `config_manager`.
  - [x] Sub-task: Load the saved slider value when the settings tab is opened.
- [x] Developer preferences (autosave, debug info)
  - [x] Sub-task: Add "Autosave" and "Debug Info" checkbuttons to the Settings tab.
  - [x] Sub-task: Implement loading and saving of these preferences via `config_manager`.

---

## 💸 Subscription Tier Logic

Tier logic is designed to control feature access based on subscription level.

All users can:

- See all tabs and tools
- Get limited functionality based on tier
- Access Weird Mode and idea generator

---

### Phase 8: ✨ User Experience & Workflow

- [x] Task: Implement an intelligent task-to-code workflow
  - [x] Sub-task: Add "Gen Code" button to each task in the Tasks Tab.
  - [x] Sub-task: Implement a communication channel between the Tasks and Edit tabs.
  - [x] Sub-task: Automatically trigger AI code generation when the button is clicked.
  - [x] Sub-task: Automatically mark the task as complete when the generated code is applied.
- [x] Task: Implement intelligent file naming for generated code
  - [x] Sub-task: Update the AI prompt to request a suggested filename in a JSON response.
  - [x] Sub-task: Pre-populate the "Save As" dialog with the AI-suggested filename.
- [x] Task: Add a right-click context menu to the file tree
  - [x] Sub-task: Implement "New File", "New Folder", "Rename", and "Delete" actions.
  - [x] Sub-task: Add confirmation dialogs for destructive actions like deletion.
- [x] Task: Add a persistent status bar for user feedback
  - [x] Sub-task: Implement a status bar widget in the main application window.
  - [x] Sub-task: Create a centralized `update_status` method.
  - [x] Sub-task: Integrate status updates for key actions (saving, opening files, etc.).
- [x] Task: Add a first-run welcome/tutorial experience
  - [x] Sub-task: Implement a `has_run_before` check in the application config.
  - [x] Sub-task: Generate a `getting_started.md` file for new projects on the first run.
  - [x] Sub-task: Automatically open the welcome file in the editor.

---

## 🌟 Current Focus: MVP Complete

- All core features from the initial roadmap are implemented.
- The focus is now on stabilization, bug fixing, and planning for V4.
