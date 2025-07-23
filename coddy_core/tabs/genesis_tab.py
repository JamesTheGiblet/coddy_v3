import tkinter as tk
from tkinter import ttk
import threading
import os
import logging

# Set up logging
LOG_DIR = r"C:\Users\gilbe\Documents\GitHub\coddy_v3\coddy_core\log"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "genesis_tab.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)
class GenesisTab(tk.Frame):
    """
    The UI for the Genesis tab, where users chat with the AI to build the project foundation.
    """
    def __init__(self, master, colors, config, ai_engine, main_app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colors = colors
        self.config(bg=self.colors['bg'])
        self.app_config = config
        self.ai_engine = ai_engine
        self.main_app = main_app # Store reference to main application
        self.is_ready_to_generate = False
        self.readme_generated = False

        self._create_widgets()
        if self.ai_engine:
            try:
                self.ai_engine.start_new_chat()
                self._display_initial_chat_history()
                logger.info("GenesisTab initialized with new AI chat session.")
            except Exception as e:
                logger.exception("Failed to start AI chat session on initialization.")
                self._add_message("Coddy", f"Error initializing AI chat: {e}\nPlease check your API key in Settings and restart.")
        else:
            self._initial_greeting() # Fallback if no AI engine
            logger.warning("GenesisTab initialized without an AI engine.")
        self._update_project_status_button()

    def _create_widgets(self):
        """Creates and lays out the widgets for the genesis tab."""
        # Use pack consistently as the parent frame is packed.

        # Input frame at the bottom
        input_frame = tk.Frame(self)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Buttons frame within the input frame
        buttons_frame = tk.Frame(input_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=(10, 0))

        # User input entry within the input frame
        self.user_input = tk.Entry(input_frame, relief=tk.FLAT,
                                   highlightthickness=1)
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

        # Chat history display
        self.chat_history = tk.Text(self, wrap=tk.WORD, relief=tk.FLAT, borderwidth=0, state=tk.DISABLED,
                                    padx=10, pady=10, font=("Helvetica", 11))
        self.chat_history.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Configure tags for chat styling
        self.chat_history.tag_configure("sender", font=("Helvetica", 11, "bold"))

        # Send button
        self.send_button = tk.Button(buttons_frame, text="Send", command=self._on_send,
                                     relief=tk.FLAT, borderwidth=0, padx=10, pady=2, cursor="hand2")
        self.send_button.pack(side=tk.LEFT)

        # Weird Idea button
        self.weird_button = tk.Button(buttons_frame, text="Weird Idea", command=self._on_weird_idea,
                                      relief=tk.FLAT, borderwidth=0, padx=10, pady=2, cursor="hand2")
        self.weird_button.pack(side=tk.LEFT, padx=(5, 0))

        # Clear Chat button
        self.clear_button = tk.Button(buttons_frame, text="Clear Chat", command=self._clear_chat,
                                      relief=tk.FLAT, borderwidth=0, padx=10, pady=2, cursor="hand2")
        self.clear_button.pack(side=tk.LEFT, padx=(5, 0))

        # Generate README button
        self.generate_button = tk.Button(buttons_frame, text="Generate README", command=self._on_generate_readme,
                                         relief=tk.FLAT, borderwidth=0, padx=10, pady=2, cursor="hand2", state=tk.DISABLED)
        self.generate_button.pack(side=tk.LEFT, padx=(5, 0))

        # Generate Roadmap button
        self.roadmap_button = tk.Button(buttons_frame, text="Generate Roadmap", command=self._on_generate_roadmap,
                                        relief=tk.FLAT, borderwidth=0, padx=10, pady=2, cursor="hand2", state=tk.DISABLED)
        self.roadmap_button.pack(side=tk.LEFT, padx=(5, 0))

        # Start Project button
        self.start_project_button = tk.Button(buttons_frame, text="🚀 Start Project", command=self._on_start_project,
                                              relief=tk.FLAT, borderwidth=0, padx=10, pady=2, cursor="hand2", state=tk.DISABLED)
        self.start_project_button.pack(side=tk.LEFT, padx=(5, 0))

    def _initial_greeting(self):
        """Displays a welcome message in the chat history."""
        greeting = "Welcome to the Genesis Chamber.\n\nWhat are we building today? Describe your idea, and I'll help you create a project roadmap."
        self._add_message("Coddy", greeting)

    def _display_initial_chat_history(self):
        """Populates the chat history with the initial messages from the AI engine."""
        if not self.ai_engine or not self.ai_engine.chat:
            return
        
        # The history starts with the system prompt, which we don't show.
        # The second message is the AI's greeting.
        for message in self.ai_engine.chat.history[1:]: # Skip the system prompt
            sender = "Coddy" if message.role == 'model' else "You"
            self._add_message(sender, message.parts[0].text)

    def _update_project_status_button(self):
        """Checks if the project has been started and updates the button accordingly."""
        main_py_path = os.path.join(self.main_app.project_path, "main.py")
        roadmap_path = os.path.join(self.main_app.project_path, "roadmap.md")

        project_started = os.path.exists(main_py_path)
        roadmap_exists = os.path.exists(roadmap_path)

        if not roadmap_exists:
            self.start_project_button.config(state=tk.DISABLED)
            return

        if project_started:
            self.start_project_button.config(text="✅ Continue Project", state=tk.NORMAL)
        else:
            self.start_project_button.config(text="🚀 Start Project", state=tk.NORMAL)

    def _add_message(self, sender, message):
        """Adds a message to the chat history text widget."""
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.insert(tk.END, f"{sender}:\n", ("sender",))
        self.chat_history.insert(tk.END, f"{message}\n\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END) # Scroll to the bottom

    def _toggle_input_widgets(self, enabled=True):
        """Enables or disables all user input widgets."""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.send_button.config(state=state)
        self.weird_button.config(state=state)
        self.clear_button.config(state=state)
        # Only enable generate/roadmap buttons if their conditions are met
        if enabled and self.is_ready_to_generate and not self.readme_generated:
            self.generate_button.config(state=tk.NORMAL)
        else:
            self.generate_button.config(state=tk.DISABLED)
        
        if enabled and self.readme_generated:
            self.roadmap_button.config(state=tk.NORMAL)
        else:
            self.roadmap_button.config(state=tk.DISABLED)

        self._update_project_status_button() # This handles the start project button state

    def _submit_to_ai(self, prompt, generation_type='chat'):
        """Handles the AI call in a separate thread to avoid freezing the UI."""
        if not self.ai_engine:
            logger.error("Attempted to submit to AI, but no engine is configured.")
            self._add_message("Coddy", "AI Engine not configured. Please check your .env file for a valid GEMINI_API_KEY.")
            return

        logger.info(f"Submitting prompt for {generation_type}: {prompt[:70]}...")
        self._toggle_input_widgets(enabled=False)

        if generation_type == 'chat':
            self._add_message("Coddy", "Thinking...")

        thread = threading.Thread(target=self._get_ai_response_threaded, args=(prompt, generation_type))
        thread.start()

    def _get_ai_response_threaded(self, prompt, generation_type):
        """The function that runs in a separate thread to call the AI."""
        try:
            response = self.ai_engine.get_chat_response(prompt)
            self.after(0, self._update_ui_with_response, response, generation_type)
        except Exception as e:
            logger.exception(f"Error getting AI response for {generation_type}.")
            error_message = f"Sorry, an error occurred: {e}"
            self.after(0, self._handle_ai_error, error_message)

    def _handle_ai_error(self, error_message):
        """Displays an error message in the chat and re-enables the UI."""
        # Remove the "Thinking..." message
        self.chat_history.config(state=tk.NORMAL)
        last_line_start = self.chat_history.index("end-3l")
        self.chat_history.delete(last_line_start, "end-1c")
        self.chat_history.config(state=tk.DISABLED)

        self._add_message("Coddy", error_message)
        self._toggle_input_widgets(enabled=True)

    def _update_ui_with_response(self, response, generation_type):
        """Updates the chat with the AI's response and re-enables buttons."""
        if generation_type == 'chat':
            # Remove the "Thinking..." message by replacing the last entry
            self.chat_history.config(state=tk.NORMAL)
            last_line_start = self.chat_history.index("end-3l")
            self.chat_history.delete(last_line_start, "end-1c")
            self.chat_history.config(state=tk.DISABLED)

        if generation_type == 'readme':
            logger.info("README.md generated successfully.")
            self.main_app.save_readme(response)
            self.readme_generated = True
            self._add_message("Coddy", "I've generated the `README.md` and saved it to your project folder. You can see it in the file tree and the 'Edit' tab.\n\nAre you happy to proceed with generating a detailed `roadmap.md` based on this information? If so, click 'Generate Roadmap'.")
        elif generation_type == 'roadmap':
            logger.info("roadmap.md generated successfully.")
            self.main_app.save_roadmap(response)
            self._update_project_status_button()
            self._add_message("Coddy", "The `roadmap.md` has been generated and saved. The project foundation is now complete!")
        elif generation_type == 'chat':
            logger.info("Received chat response from AI.")
            if "[READY_TO_GENERATE]" in response:
                self.is_ready_to_generate = True
                # Combine the AI's response with the call to action into a single message
                clean_response = response.replace("[READY_TO_GENERATE]", "").strip()
                full_message = (f"{clean_response}\n\nI think I have enough to get started. "
                                "Feel free to add more details, or click 'Generate README' when you're ready!")
                self._add_message("Coddy", full_message)
            else:
                self._add_message("Coddy", response)

        self._toggle_input_widgets(enabled=True)

    def _on_send(self):
        """Handles the user clicking the 'Send' button."""
        user_message = self.user_input.get()
        if user_message.strip():
            self._add_message("You", user_message)
            self.user_input.delete(0, tk.END)
            self._submit_to_ai(user_message)

    def _on_weird_idea(self):
        """Handles the user clicking the 'Weird Idea' button."""
        logger.info("'Weird Idea' button clicked.")
        prompt = "Give me a weird, unconventional, and creative idea for a software project. Something that sounds fun to build."
        self._submit_to_ai(prompt)

    def _clear_chat(self):
        """Clears the chat history and resets the Genesis session."""
        logger.info("Clear Chat button clicked, session reset.")
        # Clear the text widget
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete('1.0', tk.END)
        self.chat_history.config(state=tk.DISABLED)

        # Reset state
        self.is_ready_to_generate = False
        self.readme_generated = False

        # Restart AI session and display greeting
        if self.ai_engine:
            try:
                self.ai_engine.start_new_chat()
                self._display_initial_chat_history()
            except Exception as e:
                logger.exception("Failed to start new AI chat session after clearing.")
                self._add_message("Coddy", f"Error re-initializing AI chat: {e}")
        else:
            self._initial_greeting()

        # Update UI state
        self._toggle_input_widgets(enabled=True)

    def _on_start_project(self):
        """Handles the user clicking the 'Start/Continue Project' button."""
        main_py_path = os.path.join(self.main_app.project_path, "main.py")

        if os.path.exists(main_py_path):
            # "Continue Project" was clicked
            logger.info("'Continue Project' clicked.")
            self._add_message("Coddy", "Let's get back to it! Switching to the Edit tab...")
            self.main_app.notebook.select(self.main_app.tab_frames["Edit"])
            # Ensure the file is loaded in the editor
            self.main_app.edit_tab.load_file(main_py_path)
        else:
            logger.info("'Start Project' clicked.")
            # "Start Project" was clicked
            self._add_message("Coddy", "Great! I'm creating a `main.py` file for you and opening it in the Edit tab.")
            boilerplate_content = ("# Welcome to your new Coddy project!\n"
                                 "# This is your main entry point.\n\n"
                                 "def main():\n"
                                 "    print(\"Hello, Coddy World!\")\n\n"
                                 "if __name__ == \"__main__\":\n"
                                 "    main()\n")
            self.main_app.create_and_open_file("main.py", content=boilerplate_content)
        self._update_project_status_button()

    def _on_generate_readme(self):
        """Handles the user clicking the 'Generate README' button."""
        logger.info("'Generate README' button clicked.")
        self._add_message("Coddy", "Okay, I'm generating the README.md file based on our conversation. This might take a moment...")
        final_prompt = (
            "Based on our entire conversation history, generate a complete and well-structured README.md file. "
            "The README should be in Markdown format and include sections for the project title, a one-line description, "
            "core features, and a suggested tech stack. Do not include any conversational text, just the raw Markdown content. "
            "The structure should be as follows:\n\n"
            "# 📦 [Project Name]\n\n"
            "**A creative and descriptive one-line tagline for the project.**\n\n"
            "---\n\n"
            "## 🧠 Concept\n\n"
            "A paragraph explaining the core idea and 'vibe' of the project. Elaborate on the user's key ideas (e.g., the type of humor, the target audience).\n\n"
            "---\n\n"
            "## ✨ Key Features\n\n"
            "A detailed bulleted list of the main features. Expand on the points from our conversation. For example:\n"
            "*   **Pun-Powered Time-Telling:** Explain how puns will be integrated into the clock face design.\n"
            "*   **Retro-Themed Styles:** Describe the visual aesthetic and the idea of multiple clock faces.\n"
            "*   **Silly & Engaging Tone:** Mention the target audience and the overall humorous feel.\n\n"
            "---\n\n"
            "## 🔧 Tech Stack\n\n"
            "A bulleted list of the chosen technologies, including the specific GUI framework discussed."
        )
        self._submit_to_ai(final_prompt, generation_type='readme')

    def _on_generate_roadmap(self):
        """Handles the user clicking the 'Generate Roadmap' button."""
        logger.info("'Generate Roadmap' button clicked.")
        self._add_message("Coddy", "Excellent! I'm now generating the `roadmap.md` file. This might take a moment...")
        roadmap_rules = """
You are a Praximous business strategic development planner. Your task is to generate a detailed, structured, and actionable `roadmap.md` file based on our entire conversation history. The roadmap should be comprehensive enough for a development team to follow.

Use the following structure and rules:

# 🛣️ [Project Name] Roadmap

A one-sentence summary of the project's goal.

---

## ✅ MVP Milestones

Break down the core features into logical, sequential phases. Each phase should have a clear title and a checklist of specific, actionable tasks. Infer sub-tasks from the feature descriptions (e.g., 'Parental controls' implies UI, logic, and storage tasks).

### Phase 1: 🏗️ Core Setup & Foundation
- [ ] Task: Set up basic project structure (folders, main files).
- [ ] Task: Initialize the chosen GUI framework (e.g., Tkinter).
- [ ] Task: Implement the theme system (Light/Dark/Weird).

### Phase 2: ⏰ Core Feature Implementation
- [ ] Task: Implement the main clock display.
- [ ] Task: Develop the logic for the primary humorous time-telling mechanism (e.g., pun generation).
- [ ] Task: Create the system for handling multiple clock faces.

### Phase 3: 🎨 UI & User Experience
- [ ] Task: Design and implement the retro-style clock faces.
- [ ] Task: Integrate the pun-based text/designs into the UI.
- [ ] Task: Ensure the application has a polished, silly, and engaging feel.

(Add more phases as needed based on the conversation.)

---

## 🚀 Future Enhancements

List the features discussed for future versions. Group them into logical categories if possible.

### UI & Customization
- [ ] Feature: More diverse and customizable clock faces.
- [ ] Feature: Ability for users to add their own puns or jokes.

### Functionality
- [ ] Feature: Cross-platform support (macOS, Linux).
- [ ] Feature: Advanced alarm/timer features.

(Add more categories and features as discussed.)

---

## 🔧 Tech Stack Summary

Provide a clear, bulleted list of the decided-upon technologies.

- **Language**: [e.g., Python]
- **GUI Framework**: [e.g., Tkinter]
- **Key Libraries**: [e.g., Pillow for images, if discussed]

---

## 🤝 Contribution Guidelines

Include a brief, standard section encouraging contributions.

- "Contributions are welcome! Please open an issue to discuss a new feature or submit a pull request for bug fixes."

---

Generate only the raw Markdown content for the `roadmap.md` file. Do not include any conversational text.
"""
        self._submit_to_ai(roadmap_rules, generation_type='roadmap')

    def apply_colors(self, colors):
        """Applies a new color theme to the genesis tab and its children."""
        self.colors = colors
        self.config(bg=colors['bg'])
        self.chat_history.config(bg=colors['bg'], fg=colors['fg'])
        self.chat_history.tag_configure("sender", foreground=colors['accent'])
        self.winfo_children()[1].config(bg=colors['bg']) # input_frame
        self.winfo_children()[1].winfo_children()[1].config(bg=colors['bg']) # buttons_frame
        self.user_input.config(bg=colors['bg'], fg=colors['fg'],
                               insertbackground=colors['fg'],
                               highlightbackground=colors['quote'])
        self.send_button.config(bg=colors['accent'], fg=colors['button_fg'],
                                activebackground=colors['accent_active'],
                                activeforeground=colors['button_fg'])
        self.weird_button.config(bg=colors['bg'], fg=colors['quote'],
                                 activebackground=colors['bg'], activeforeground=colors['fg'])
        self.clear_button.config(bg=colors['bg'], fg=colors['quote'],
                                 activebackground=colors['bg'], activeforeground=colors['fg'])
        self.generate_button.config(bg=colors['accent'], fg=colors['button_fg'],
                                    activebackground=colors['accent_active'],
                                    activeforeground=colors['button_fg'])
        self.roadmap_button.config(bg=colors['accent'], fg=colors['button_fg'],
                                   activebackground=colors['accent_active'],
                                   activeforeground=colors['button_fg'])
        self.start_project_button.config(bg=colors['accent'], fg=colors['button_fg'],
                                         activebackground=colors['accent_active'],
                                         activeforeground=colors['button_fg'])