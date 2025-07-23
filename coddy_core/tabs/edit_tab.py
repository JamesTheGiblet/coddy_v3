import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext, filedialog
import os
import threading
import re
import logging
from .. import subscription
from ..ui.code_editor import CodeEditor

# Set up logging
LOG_DIR = r"C:\Users\gilbe\Documents\GitHub\coddy_v3\coddy_core\log"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "edit_tab.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

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
        self.active_ai_task = None # Track if AI was triggered from Tasks tab
        self.suggested_filename = None

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

        # Replace the basic Text widget with our new CodeEditor
        self.code_editor = CodeEditor(editor_frame, self.colors)
        self.code_editor.pack(fill="both", expand=True)
        self.code_editor.text.bind("<<Modified>>", self._on_text_modified, add=True)

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
        self.suggested_filename = None
        self.current_file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.load_file_content(content, file_path=file_path, highlight=True)
        except Exception as e:
            error_message = f"Could not read file:\n{file_path}\n\nError: {e}"
            logger.error(error_message)
            self.load_file_content(error_message, file_path=None)

    def load_file_content(self, content, file_path=None, highlight=False):
        """Loads raw string content into the text editor."""
        self.suggested_filename = None
        self.current_file_path = file_path
        self.code_editor.text.delete('1.0', tk.END)
        self.code_editor.text.insert('1.0', content)
        self.code_editor.text.edit_reset() # Clear the undo stack for the new file
        if highlight:
            self.code_editor.trigger_highlight()
        self.code_editor.text.edit_modified(False) # Reset modified flag to prevent autosave on load

    def save_current_file(self, autosave=False):
        """Saves the content of the text editor to the current file.
           If no file is open, prompts the user with a 'Save As' dialog.
        """
        path_to_save = self.current_file_path
        is_new_file = False

        if not path_to_save:
            if autosave: # Don't show 'Save As' for autosave on an untitled buffer
                return
            
            is_new_file = True
            path_to_save = filedialog.asksaveasfilename(
                initialdir=self.app_logic.project_path,
                title="Save New File",
                initialfile=self.suggested_filename,
                defaultextension=".py",
                filetypes=[("Python Files", "*.py"), ("Text Files", "*.txt"), ("All Files", "*.*")],
                parent=self
            )
            if not path_to_save:
                return # User cancelled the dialog
            
            self.current_file_path = path_to_save
            # Clear the suggested name after it has been used
            self.suggested_filename = None

        try:
            content = self.code_editor.text.get("1.0", "end-1c")
            with open(path_to_save, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if autosave:
                self.app_logic.debug_print(f"Autosaved: {os.path.basename(path_to_save)}")
            else:
                self.app_logic.update_status(f"Saved: {os.path.basename(path_to_save)}")
            if is_new_file:
                self.app_logic.refresh_file_tree()
        except Exception as e:
            logger.error(f"Could not save file: {path_to_save}\nError: {e}")
            messagebox.showerror("Save Error", f"Could not save file:\n{path_to_save}\n\nError: {e}")

    def _on_text_modified(self, event=None):
        """Handles the event when the text editor content is modified."""
        # Check if autosave is enabled in the application's config
        if self.app_logic.app_config.get('developer_autosave', False):
            self.save_current_file(autosave=True)

        # The <<Modified>> event is only fired once until the modified flag is reset.
        # We must reset it to be able to catch the next modification.
        try:
            if self.code_editor.text.winfo_exists():
                self.code_editor.text.edit_modified(False)
        except tk.TclError:
            logger.warning("Text widget destroyed during shutdown.")
            pass # Widget might be destroyed during shutdown

    def get_ai_suggestion(self):
        """
        Gets the selected code, the user's task, and asks the AI for a suggestion in a new thread.
        """
        # This is a manual request, so clear any task tracking
        self.active_ai_task = None
        user_prompt = self.ai_task_entry.get()
        self._run_suggestion_flow(user_prompt)

    def execute_ai_suggestion(self, task_text):
        """
        Programmatically triggers the AI suggestion flow for a specific task.
        """
        self.set_ai_task(task_text)
        self.active_ai_task = task_text
        self._run_suggestion_flow(task_text)

    def _run_suggestion_flow(self, prompt):
        """
        Core logic to get code, check tiers, and run the AI suggestion thread.
        """
        if not prompt:
            messagebox.showwarning("Input Required", "Please enter a task for the AI (e.g., 'refactor this' or 'add comments').")
            return

        # --- Tier Check ---
        if not subscription.is_feature_enabled(self.app_logic.active_tier, subscription.Feature.AI_SUGGESTION):
            messagebox.showinfo(
                "Upgrade Required",
                f"The 'Get Suggestion' feature is available for {subscription.SubscriptionTier.CREATOR.value}+ subscribers.\n\n"
                f"You can change your tier in the Settings tab for testing."
            )
            return

        try:
            # Get selected text, or all text if nothing is selected
            self.selection_indices = (self.code_editor.text.index(tk.SEL_FIRST), self.code_editor.text.index(tk.SEL_LAST))
            code_snippet = self.code_editor.text.get(self.selection_indices[0], self.selection_indices[1])
            self.suggestion_scope = 'selection'
        except tk.TclError:
            code_snippet = self.code_editor.text.get("1.0", tk.END)
            self.suggestion_scope = 'all'
            self.selection_indices = None

        self._toggle_ai_widgets(enabled=False)

        threading.Thread(
            target=self._run_ai_suggestion_thread,
            args=(prompt, code_snippet),
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

        code_snippet = self.code_editor.text.get("1.0", tk.END)
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
            logger.error(f"AI refactor error: {e}")
            self.after(0, messagebox.showerror, "AI Error", f"An error occurred during refactoring:\n{e}")
        finally:
            self.after(0, self._toggle_ai_widgets, True)

    def _run_ai_suggestion_thread(self, user_prompt, code_snippet):
        """
        Worker function that calls the AI engine and schedules the result to be displayed.
        """
        try:
            # AI now returns a dictionary
            response_data = self.app_logic.ai_engine.get_code_suggestion(user_prompt, code_snippet)
            
            # Set the suggested filename if the AI provided one
            self.suggested_filename = response_data.get('filename')
            
            # Get the code to display
            code_suggestion = response_data.get('code', "AI response was not in the expected format.")

            self.after(0, self._display_suggestion, code_suggestion)
        except Exception as e:
            logger.error(f"AI suggestion error: {e}")
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
                self.code_editor.text.delete(start, end)
                self.code_editor.text.insert(start, new_content.strip())
            elif self.suggestion_scope == 'all':
                self.code_editor.text.delete("1.0", tk.END)
                self.code_editor.text.insert("1.0", new_content.strip())

            # If this suggestion was tied to a specific task, mark it as complete
            if self.active_ai_task:
                self.app_logic.mark_task_as_complete(self.active_ai_task)
                self.active_ai_task = None # Clear after use
            
            # Trigger highlight after applying changes
            self.code_editor.trigger_highlight()
            
            window.destroy()
        except Exception as e:
            logger.error(f"Could not apply changes: {e}")
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

    def set_ai_task(self, task_text):
        """Sets the text of the AI task entry widget."""
        self.ai_task_entry.delete(0, tk.END)
        self.ai_task_entry.insert(0, task_text)
        self.ai_task_entry.focus_set()

    def apply_colors(self, colors):
        """Applies a new color theme to the edit tab and its children."""
        self.colors = colors
        self.config(bg=colors['bg'])
        self.code_editor.apply_colors(colors)
