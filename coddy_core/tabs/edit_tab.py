import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext
import threading

class EditTab(tk.Frame):
    """
    The UI for the Edit tab, where users can view/edit files and interact with the AI.
    """
    def __init__(self, master, colors, app_logic, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colors = colors
        self.app_logic = app_logic # This is the MainApplication instance
        self.config(bg=self.colors['bg'])

        self._create_widgets()
        self.apply_colors(self.colors) # Apply initial colors

    def _create_widgets(self):
        """Creates and lays out the widgets for the edit tab."""
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # --- Editor Frame ---
        editor_frame = tk.Frame(self, bg=self.colors['bg'])
        editor_frame.grid(row=0, column=0, sticky="nsew")
        editor_frame.rowconfigure(0, weight=1)
        editor_frame.columnconfigure(0, weight=1)

        self.text_editor = tk.Text(editor_frame, wrap=tk.WORD, relief=tk.FLAT, borderwidth=0)
        scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        self.text_editor.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- AI Interaction Frame ---
        ai_frame = ttk.Frame(self)
        ai_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))

        ai_label = ttk.Label(ai_frame, text="AI Task:")
        ai_label.pack(side="left", padx=(0, 5))

        self.ai_task_entry = ttk.Entry(ai_frame, font=("Segoe UI", 10))
        self.ai_task_entry.pack(side="left", fill="x", expand=True)

        self.get_suggestion_button = ttk.Button(ai_frame, text="💡 Get Suggestion", command=self.get_ai_suggestion)
        self.get_suggestion_button.pack(side="left", padx=(5, 0))

    def load_file(self, file_path):
        """Loads content from a file into the text editor."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.load_file_content(content)
        except Exception as e:
            error_message = f"Could not read file:\n{file_path}\n\nError: {e}"
            self.load_file_content(error_message)

    def load_file_content(self, content):
        """Loads raw string content into the text editor."""
        self.text_editor.delete('1.0', tk.END)
        self.text_editor.insert('1.0', content)

    def get_ai_suggestion(self):
        """
        Gets the selected code, the user's task, and asks the AI for a suggestion in a new thread.
        """
        user_prompt = self.ai_task_entry.get()
        if not user_prompt:
            messagebox.showwarning("Input Required", "Please enter a task for the AI (e.g., 'refactor this' or 'add comments').")
            return

        try:
            # Get selected text, or all text if nothing is selected
            code_snippet = self.text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            code_snippet = self.text_editor.get("1.0", tk.END)

        if not code_snippet.strip():
            messagebox.showwarning("Code Required", "Please select some code or open a file to get a suggestion.")
            return

        self._toggle_ai_widgets(enabled=False)

        threading.Thread(
            target=self._run_ai_suggestion_thread,
            args=(user_prompt, code_snippet),
            daemon=True
        ).start()

    def _run_ai_suggestion_thread(self, user_prompt, code_snippet):
        """
        Worker function that calls the AI engine and schedules the result to be displayed.
        """
        try:
            suggestion = self.app_logic.ai_engine.get_code_suggestion(user_prompt, code_snippet)
            self.after(0, self._display_suggestion, suggestion)
        except Exception as e:
            self.after(0, messagebox.showerror, "AI Error", f"An error occurred while getting a suggestion:\n{e}")
        finally:
            self.after(0, self._toggle_ai_widgets, True)

    def _display_suggestion(self, suggestion):
        """
        Displays the AI's suggestion in a new Toplevel window.
        """
        suggestion_window = Toplevel(self)
        suggestion_window.title("AI Suggestion")
        suggestion_window.geometry("700x500")

        suggestion_window.transient(self.winfo_toplevel())
        suggestion_window.grab_set()

        st = scrolledtext.ScrolledText(suggestion_window, wrap=tk.WORD, padx=5, pady=5)
        st.pack(expand=True, fill="both")
        st.insert(tk.END, suggestion)
        st.config(state="disabled")

        self.winfo_toplevel().wait_window(suggestion_window)

    def _toggle_ai_widgets(self, enabled):
        """Enables or disables the AI interaction widgets."""
        state = "normal" if enabled else "disabled"
        self.get_suggestion_button.config(state=state)
        self.ai_task_entry.config(state=state)
        if enabled:
            self.ai_task_entry.delete(0, tk.END)

    def apply_colors(self, colors):
        """Applies a new color theme to the edit tab and its children."""
        self.colors = colors
        self.config(bg=colors['bg'])
        self.text_editor.config(bg=colors['bg'], fg=colors['fg'],
                                insertbackground=colors['fg'],
                                selectbackground=colors['accent'])