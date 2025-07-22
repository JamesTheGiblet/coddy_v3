import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext
import threading
from .. import subscription

class EditTab(tk.Frame):
    """
    The UI for the Edit tab, where users can view/edit files and interact with the AI.
    """
    def __init__(self, master, colors, app_logic, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colors = colors
        self.app_logic = app_logic # This is the MainApplication instance
        self.config(bg=self.colors['bg'])

        # State for the currently edited file
        # and suggestion scope
        self.current_file_path = None
        self.suggestion_scope = None
        self.selection_indices = None

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

        self.text_editor = tk.Text(editor_frame, wrap=tk.WORD, relief=tk.FLAT, borderwidth=0, undo=True)
        scrollbar = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        self.text_editor.config(yscrollcommand=scrollbar.set)
        self.text_editor.bind("<<Modified>>", self._on_text_modified)

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

        self.refactor_button = ttk.Button(ai_frame, text="✨ Full Refactor", command=self.get_full_refactor)
        self.refactor_button.pack(side="left", padx=(5, 0))

        self.save_button = ttk.Button(ai_frame, text="💾 Save File", command=lambda: self.save_current_file(autosave=False))
        self.save_button.pack(side="left", padx=(5, 0))

    def load_file(self, file_path):
        """Loads content from a file into the text editor."""
        self.current_file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.load_file_content(content, file_path=file_path)
        except Exception as e:
            error_message = f"Could not read file:\n{file_path}\n\nError: {e}"
            self.load_file_content(error_message, file_path=None)

    def load_file_content(self, content, file_path=None):
        """Loads raw string content into the text editor."""
        self.current_file_path = file_path
        self.text_editor.delete('1.0', tk.END)
        self.text_editor.insert('1.0', content)
        self.text_editor.edit_reset() # Clear the undo stack for the new file
        self.text_editor.edit_modified(False) # Reset modified flag to prevent autosave on load

    def save_current_file(self, autosave=False):
        """Saves the content of the text editor to the current file."""
        if not self.current_file_path:
            if not autosave: # Only show warning on manual save
                messagebox.showwarning("Save Error", "No file is currently open to save.")
            return
        try:
            content = self.text_editor.get("1.0", "end-1c") # Exclude the final newline
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if autosave:
                self.app_logic.debug_print(f"Autosaved: {self.current_file_path}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file:\n{self.current_file_path}\n\nError: {e}")

    def _on_text_modified(self, event=None):
        """Handles the event when the text editor content is modified."""
        # Check if autosave is enabled in the application's config
        if self.app_logic.app_config.get('developer_autosave', False):
            self.save_current_file(autosave=True)

        # The <<Modified>> event is only fired once until the modified flag is reset.
        # We must reset it to be able to catch the next modification.
        try:
            # Check if widget exists before trying to modify it
            if self.text_editor.winfo_exists():
                self.text_editor.edit_modified(False)
        except tk.TclError:
            pass # Widget might be destroyed during shutdown

    def get_ai_suggestion(self):
        """
        Gets the selected code, the user's task, and asks the AI for a suggestion in a new thread.
        """
        # --- Tier Check ---
        if not subscription.is_feature_enabled(self.app_logic.active_tier, subscription.Feature.AI_SUGGESTION):
            messagebox.showinfo(
                "Upgrade Required",
                f"The 'Get Suggestion' feature is available for {subscription.SubscriptionTier.CREATOR.value}+ subscribers.\n\n"
                f"You can change your tier in the Settings tab for testing."
            )
            return

        user_prompt = self.ai_task_entry.get()
        if not user_prompt:
            messagebox.showwarning("Input Required", "Please enter a task for the AI (e.g., 'refactor this' or 'add comments').")
            return

        try:
            # Get selected text, or all text if nothing is selected
            self.selection_indices = (self.text_editor.index(tk.SEL_FIRST), self.text_editor.index(tk.SEL_LAST))
            code_snippet = self.text_editor.get(self.selection_indices[0], self.selection_indices[1])
            self.suggestion_scope = 'selection'
        except tk.TclError:
            code_snippet = self.text_editor.get("1.0", tk.END)
            self.suggestion_scope = 'all'
            self.selection_indices = None

        if not code_snippet.strip():
            messagebox.showwarning("Code Required", "Please select some code or open a file to get a suggestion.")
            return

        self._toggle_ai_widgets(enabled=False)

        threading.Thread(
            target=self._run_ai_suggestion_thread,
            args=(user_prompt, code_snippet),
            daemon=True
        ).start()

    def get_full_refactor(self):
        """
        Gets the full code from the editor and asks the AI for a full semantic refactor.
        """
        # --- Tier Check ---
        if not subscription.is_feature_enabled(self.app_logic.active_tier, subscription.Feature.FULL_REFACTOR):
            messagebox.showinfo(
                "Upgrade Required",
                f"The 'Full Refactor' feature is available for {subscription.SubscriptionTier.ARCHITECT.value}+ subscribers.\n\n"
                f"You can change your tier in the Settings tab for testing."
            )
            return

        code_snippet = self.text_editor.get("1.0", tk.END)
        if not code_snippet.strip():
            messagebox.showwarning("Code Required", "Please open a file to refactor.")
            return

        # This is a whole-file operation, so we set the scope accordingly.
        self.suggestion_scope = 'all'
        self.selection_indices = None

        self._toggle_ai_widgets(enabled=False)

        threading.Thread(
            target=self._run_ai_refactor_thread,
            args=(code_snippet,),
            daemon=True
        ).start()

    def _run_ai_refactor_thread(self, code_snippet):
        """
        Worker function that calls the AI engine for a full refactor.
        """
        try:
            suggestion = self.app_logic.ai_engine.get_full_refactor(code_snippet)
            self.after(0, self._display_suggestion, suggestion)
        except Exception as e:
            self.after(0, messagebox.showerror, "AI Error", f"An error occurred during refactoring:\n{e}")
        finally:
            self.after(0, self._toggle_ai_widgets, True)

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
        Displays the AI's suggestion in a new Toplevel window with apply/cancel buttons.
        """
        suggestion_window = Toplevel(self)
        suggestion_window.title("AI Suggestion")
        suggestion_window.geometry("700x500")

        suggestion_window.transient(self.winfo_toplevel())
        suggestion_window.grab_set()

        # Frame for text editor and scrollbar
        text_frame = tk.Frame(suggestion_window)
        text_frame.pack(expand=True, fill="both", padx=10, pady=(10, 0))

        st = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, padx=5, pady=5, undo=True)
        st.pack(expand=True, fill="both")
        st.insert(tk.END, suggestion)

        # Frame for buttons
        button_frame = ttk.Frame(suggestion_window)
        button_frame.pack(fill="x", padx=10, pady=10)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=suggestion_window.destroy)
        cancel_button.pack(side="right")

        apply_button = ttk.Button(button_frame, text="Apply & Close", command=lambda: self._apply_suggestion(st.get("1.0", tk.END), suggestion_window))
        apply_button.pack(side="right", padx=(0, 5))

        self.winfo_toplevel().wait_window(suggestion_window)

    def _apply_suggestion(self, new_content, window):
        """Applies the suggestion from the popup to the main editor."""
        # --- Tier Check ---
        if not subscription.is_feature_enabled(self.app_logic.active_tier, subscription.Feature.APPLY_AI_EDIT):
            messagebox.showinfo(
                "Upgrade Required",
                f"Applying edits is available for {subscription.SubscriptionTier.CREATOR.value}+ subscribers.\n\n"
                f"You can change your tier in the Settings tab for testing.",
                parent=window
            )
            return

        try:
            if self.suggestion_scope == 'selection' and self.selection_indices:
                start, end = self.selection_indices
                self.text_editor.delete(start, end)
                self.text_editor.insert(start, new_content.strip())
            elif self.suggestion_scope == 'all':
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", new_content.strip())
            window.destroy()
        except Exception as e:
            messagebox.showerror("Apply Error", f"Could not apply changes: {e}", parent=window)

    def _toggle_ai_widgets(self, enabled):
        """Enables or disables the AI interaction widgets."""
        state = "normal" if enabled else "disabled"
        self.get_suggestion_button.config(state=state)
        self.refactor_button.config(state=state)
        self.save_button.config(state=state)
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