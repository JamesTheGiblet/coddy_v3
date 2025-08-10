## **Project: Coddy V3**

An AI-Powered Coding Assistant

#### **The Big Idea**

Starting a new project involves a ton of boilerplate. You have to create the file structure, write a `README`, plan a roadmap, set up your environment... it's all grunt work that gets in the way of the actual *idea*.

Coddy is a desktop app designed to be your AI coding partner. It handles the boring setup and repetitive tasks so you can focus on the creative "vibe" of your project. You have an idea, you chat with Coddy, and together you build it.

> **My motto for this project:** Let the AI do the grunt work—you focus on the build.

-----

#### **What It Does (The Modules)**

Coddy is broken down into a few simple, focused modules. The active module is indicated by a pulsing **Neon Spiral** in the UI.

##### **🧬 Genesis Module (Start a Project)**

This is where every new project begins.

  * Start a new project from scratch or open an existing one.
  * Chat with the AI to brainstorm and flesh out your initial idea.
  * Automatically generate a foundational `README.md` and a project roadmap based on your chat.
  * Hit the **"Weird Idea" button** if you're stuck. It uses the AI to inject a bit of chaos and creativity.

##### **🛠️ Edit Module (Write & Refactor Code)**

Your main workspace for building.

  * A built-in file navigator and code editor.
  * Use the AI to generate new code, refactor existing blocks, add comments, or fix bugs.
  * Get inline suggestions from the AI that you can preview and apply with a click.

##### **📋 Task Module (Track Your Progress)**

Keeps you focused on the roadmap.

  * A visual tracker for all the phases and tasks you planned in the Genesis module.
  * The AI keeps a log of what's done and what's next.

##### **⚙️ Settings Module (Tweak the Settings)**

Make Coddy work your way.

  * Configure your LLM API keys (e.g., Gemini).
  * Set the UI theme: Void Black, Light, or the default "Weird" theme.
  * Adjust the **"Unorthodox Ideas" slider** from "Conservative" to "Total Chaos" to control how wild the AI's creative suggestions are.

##### **👤 Profile Module (Your Account)**

  * Login/logout functionality (future feature).
  * Manage your subscription tier (future feature).

-----

#### **The File Structure**

The project is organized to be clean and modular.

```
coddy-v3/
├── coddy_core/         # The core Python logic and UI.
│   ├── ai/             # AI integration (Gemini, etc.).
│   └── tabs/           # The code for each module's UI.
├── coddy_codes/        # This is where your new projects are saved.
├── .coddy/             # User settings and session data.
├── .env                # Your secret API keys live here.
├── roadmap.md          # The roadmap for Coddy itself.
├── requirements.txt    # Python dependencies.
├── run.py              # The script to start the app.
└── README.md           # This file.
```

-----

#### **How to Install It**

To get Coddy V3 running on your local machine:

**1. Clone the Repository:**

```bash
git clone https://github.com/yourusername/coddy-v3 # Replace with the actual repo URL
cd coddy-v3
```

**2. Set up the Python Environment:**
It's best practice to use a virtual environment.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

**3. Install Dependencies:**

```bash
pip install -r requirements.txt
```

**4. Run the App:**
From the project root, run the `run.py` script:

```bash
python run.py
```

-----

#### **How to Contribute**

This is a tool for builders. If you want to help build it, all ideas are welcome. Submit an issue, open a pull request, or suggest a new feature for the roadmap.

-----

#### **License**

This project is licensed under the **MIT License**.

This is a tool for builders who'd rather be creating than configuring. Stop wrestling with boilerplate. **Build first, ask permission never.** Let the AI do the grunt work.
