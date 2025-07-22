# 📦 Coddy V3

**Coddy V3** is your vibe-coding companion — a desktop application that fuses creative coding with AI-powered automation. Designed to free developers from repetitive tasks, Coddy leverages LLMs to help you **brainstorm**, **plan**, **generate**, **refactor**, and **evolve** projects — all while adapting to your unique coding style.

---

## 🧠 Philosophy

> "Let the AI do the grunt work — you focus on the vibes."

Coddy encourages a creative-first workflow:

* You sketch the idea
* Coddy helps turn that idea into a roadmap
* Together, you generate and refine the code

Coddy gets smarter as you use it — tracking progress, learning your preferences, and offering spontaneous (and sometimes weird) suggestions.

---

## 💻 Local-First Installable App

* Built with **Tauri** (GUI Shell) and **Python** (Core Logic)
* Cross-platform: Windows, macOS, Linux
* Fast, lightweight, and modular
* Fully local session data & settings storage

---

## ✨ Key Features

### 🧬 Genesis Tab

* Start a new project or load existing one
* Chat with the AI to shape your idea
* Auto-generate README and roadmap
* "Weird Idea" button for chaotic creativity (if enabled)

### 🛠️ Edit Tab

* View files in your project
* Edit, refactor, or generate code with LLM help
* Inline suggestions and preview before applying

### 📋 Tasks Tab

* Visual tracker of roadmap phases and tasks
* AI keeps track of what's done, what’s next
* Background worker pre-generates future steps

### ⚙️ Settings Tab

* Configure LLM API keys (OpenAI, Anthropic, etc.)
* Set theme: Light / Dark / Weird
* Adjust prompt retry count and model behavior

### 👤 Profile Menu

* Access login/logout (future feature)
* See subscription tier
* Adjust “Unorthodox Ideas” slider: conservative ↔ chaos

---

## 🧪 Subscription Tiers

| Tier | Projects  | Features Access     | Weird Mode | AI Tracking |
| ---- | --------- | ------------------- | ---------- | ----------- |
| Free | 1         | Core Only           | ❌          | ❌           |
| Pro  | Unlimited | Full                | ✅          | ✅           |
| Team | Unlimited | Collaboration, Sync | ✅          | ✅           |

Features are not API-limited — they are **functionality-limited** based on tier.

---

## 🔥 Adaptive AI Engine

Coddy learns your intent and adjusts accordingly:

* Learns from your prompts, edits, and style
* Tailors LLM output to your tone, habits, project structure
* Adjusts roadmap granularity, idea types, and UX flow

---

## 🔧 Tech Stack

* **Python 3.11+** (backend logic)
* **Tauri + Rust** (UI container)
* **JavaScript + HTML** (Tauri frontend shell)
* **SQLite / JSON** (local data storage)

---

## 🗂️ File Structure

coddy-v3/
├── src-tauri/        # Tauri UI shell
├── coddy-core/       # Python logic (AI, roadmap, editor)
│   ├── engine/
│   ├── ai/
│   └── utils/
├── assets/           # Theme files, icons, UX assets
├── .coddy/           # User session + settings
├── README.md         # Generated from Genesis Tab
├── roadmap.md        # Structured AI roadmap

---

## 🏁 Getting Started

```bash
# Clone the repo
$ git clone https://github.com/yourusername/coddy-v3
$ cd coddy-v3

# Setup Python backend
$ python -m venv .venv
$ source .venv/bin/activate  # or .venv\Scripts\activate on Windows
$ pip install -r requirements.txt

# Install Tauri dependencies
$ npm install
$ npx tauri dev
```

---

## 🚀 Status

Coddy V3 is under active development.
The current roadmap includes:

* Genesis Tab
* Roadmap generator
* File system interaction
* AI refactor engine
* Local session memory and user adaptation

---

## 🤝 Contributing

Want to contribute or test an idea? Weird ideas welcome. Submit an issue, open a PR, or suggest roadmap tasks.

---

## 📜 License

MIT

---

Ready to vibe?
Run `Coddy`, start a project, and let the ideas flow — weird or otherwise. 🧠✨
