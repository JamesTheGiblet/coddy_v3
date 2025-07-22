import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import shutil
from . import auth, config_manager, subscription, theme
from .ai.ai_engine import AIEngine
from .tabs.genesis_tab import GenesisTab
from .tabs.edit_tab import EditTab
from .tabs.settings_tab import SettingsTab
from .tabs.tasks_tab import TasksTab

class MainApplication(tk.Toplevel):
    """The main application window with file tree and tabs."""

    def __init__(self, master, project_path, theme_name='dark', file_to_open=None):
        super().__init__(master)
        self.project_path = project_path
        self.theme_name = theme_name
        self.colors = theme.get_theme(self.theme_name)
        self.app_config = config_manager.load_config()
        
        # --- Initialize AI Engine ---
        self.ai_engine = None
        gemini_api_key = config_manager.load_gemini_key()
        if gemini_api_key:
            try:
                self.ai_engine = AIEngine(api_key=gemini_api_key)
            except Exception as e:
                print(f"Failed to initialize AI Engine: {e}")
        
        # Add the loaded Gemini key to the config dict for the settings tab UI
        self.app_config['gemini_api_key'] = gemini_api_key

        # --- Initialize Subscription Tier ---
        # When logged out, the application always defaults to the FREE tier.
        # The 'active_tier' in the config is only for setting the initial
        # state of the testing dropdown in the Settings tab, not the app's functional tier.
        self.active_tier = subscription.SubscriptionTier.FREE
        self.active_tier_name = self.active_tier.value
        self.current_user = None

        self.title(f"Coddy V3 - {os.path.basename(project_path)}")
        self.geometry("1200x800")

        self._initialize_widget_holders()
        self._configure_styles()
        self._create_widgets()
        self._populate_tree()
        self._apply_colors()

        # Set the close protocol for this window
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # If a specific file was requested to be opened on launch (e.g., welcome file)
        if file_to_open:
            full_path = os.path.join(project_path, file_to_open)
            if os.path.exists(full_path):
                self.edit_tab.load_file(full_path)

        # Set initial UI state for the default (logged-out) profile
        self._update_auth_ui()

    def _configure_styles(self):
        """Configure ttk styles for the current theme."""
        style = ttk.Style(self)
        style.theme_use('clam') # A good base theme for custom styling

        # Treeview styling
        style.configure("Treeview",
                        background=self.colors['bg'],
                        foreground=self.colors['fg'],
                        fieldbackground=self.colors['bg'],
                        borderwidth=0)
        style.map('Treeview', background=[('selected', self.colors['accent'])])

        # Notebook (Tabs) styling
        style.configure("TNotebook", background=self.colors['bg'], borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=self.colors['bg'],
                        foreground=self.colors['quote'],
                        padding=[10, 5],
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", self.colors['accent'])],
                  foreground=[("selected", self.colors['button_fg'])])

        # Link-style button for login/signup switching
        style.configure("Link.TButton", foreground=self.colors['accent'], borderwidth=0, background=self.colors['bg'])
        style.map("Link.TButton", background=[('active', self.colors['bg'])])

    def _initialize_widget_holders(self):
        """Initialize holders for widgets that need to be accessed later."""
        self.tree = None
        self.notebook = None
        self.edit_tab = None
        self.settings_tab = None
        self.genesis_tab = None
        self.tasks_tab = None
        self.status_bar_label = None
        self.context_menu = None

    def _create_widgets(self):
        """Create the main layout and widgets."""
        # Paned window for resizable sections
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Left pane: File Tree
        tree_container = ttk.Frame(paned_window, width=300)
        paned_window.add(tree_container, weight=1)

        # Header for the file tree with a refresh button
        tree_header = ttk.Frame(tree_container)
        tree_header.pack(fill=tk.X, padx=2, pady=2)
        
        ttk.Label(tree_header, text="Project Files").pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(tree_header, text="🔄 Refresh", command=self.refresh_file_tree)
        refresh_button.pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(tree_container)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self._create_context_menu()

        # Right pane: Tabs
        self.notebook = ttk.Notebook(paned_window)
        paned_window.add(self.notebook, weight=3)

        # Create placeholder tabs based on README
        tab_names = ["Genesis", "Edit", "Tasks", "Settings"]
        self.tab_frames = {} # Use a dictionary to hold tab frames

        for name in tab_names:
            tab_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
            self.notebook.add(tab_frame, text=name)
            self.tab_frames[name] = tab_frame

            if name == "Edit":
                # Instantiate the self-contained EditTab
                self.edit_tab = EditTab(tab_frame, self.colors, self)
                self.edit_tab.pack(fill=tk.BOTH, expand=True)
            elif name == "Settings":
                self.settings_tab = SettingsTab(tab_frame, self.colors, self)
                self.settings_tab.pack(fill=tk.BOTH, expand=True)
            elif name == "Genesis":
                self.genesis_tab = GenesisTab(tab_frame, self.colors, self.app_config, self.ai_engine, self)
                self.genesis_tab.pack(fill=tk.BOTH, expand=True)
            elif name == "Tasks":
                self.tasks_tab = TasksTab(tab_frame, self.colors, self)
                self.tasks_tab.pack(fill=tk.BOTH, expand=True)
            else:
                placeholder = tk.Label(tab_frame, text=f"Content for {name} Tab", font=("Helvetica", 16))
                placeholder.pack(pady=50)

        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        self.tree.bind('<Button-3>', self._show_context_menu) # For Windows/Linux
        self.tree.bind('<Button-2>', self._show_context_menu) # For macOS

        # --- Status Bar ---
        status_frame = tk.Frame(self, bg=self.colors['bg'])
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=2)
        self.status_bar_label = tk.Label(status_frame, text="Ready.", anchor=tk.W, bg=self.colors['bg'], fg=self.colors['quote'])
        self.status_bar_label.pack(fill=tk.X, padx=5)

    def _create_context_menu(self):
        """Creates the right-click context menu for the file tree."""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="New File...", command=self._new_file)
        self.context_menu.add_command(label="New Folder...", command=self._new_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename...", command=self._rename_item)
        self.context_menu.add_command(label="Delete", command=self._delete_item)

    def _show_context_menu(self, event):
        """Shows the context menu on right-click."""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            # Enable item-specific actions
            self.context_menu.entryconfig("Rename...", state="normal")
            self.context_menu.entryconfig("Delete", state="normal")
        else:
            # Clicked on empty space, disable item-specific actions
            self.tree.selection_set() # Deselect everything
            self.context_menu.entryconfig("Rename...", state="disabled")
            self.context_menu.entryconfig("Delete", state="disabled")
        
        self.context_menu.post(event.x_root, event.y_root)

    def _get_selected_path(self):
        """Gets the full path of the currently selected item in the tree."""
        selected_ids = self.tree.selection()
        if not selected_ids:
            return None
        return self.tree.item(selected_ids[0], 'values')[0]

    def _rename_item(self):
        """Renames the selected file or folder."""
        path = self._get_selected_path()
        if not path: return

        dir_name, old_name = os.path.split(path)
        new_name = simpledialog.askstring("Rename", f"Enter new name for '{old_name}':", initialvalue=old_name, parent=self)

        if new_name and new_name.strip() and new_name != old_name:
            new_path = os.path.join(dir_name, new_name)
            try:
                os.rename(path, new_path)
                self.refresh_file_tree()
                self.update_status(f"Renamed to '{new_name}'")
            except OSError as e:
                messagebox.showerror("Error", f"Could not rename: {e}", parent=self)

    def _delete_item(self):
        """Deletes the selected file or folder."""
        path = self._get_selected_path()
        if not path: return

        item_name = os.path.basename(path)
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to permanently delete '{item_name}'?", parent=self):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                self.refresh_file_tree()
                self.update_status(f"Deleted '{item_name}'")
            except OSError as e:
                messagebox.showerror("Error", f"Could not delete: {e}", parent=self)

    def _new_file(self):
        """Creates a new empty file in the selected directory or project root."""
        path = self._get_selected_path()
        if path and os.path.isfile(path):
            target_dir = os.path.dirname(path)
        elif path and os.path.isdir(path):
            target_dir = path
        else:
            target_dir = self.project_path

        file_name = simpledialog.askstring("New File", "Enter name for the new file:", parent=self)
        if file_name and file_name.strip():
            new_path = os.path.join(target_dir, file_name)
            if os.path.exists(new_path):
                messagebox.showwarning("Exists", "A file with that name already exists.", parent=self)
                return
            try:
                with open(new_path, 'w') as f:
                    pass # Create empty file
                self.refresh_file_tree()
                self.update_status(f"Created file: {file_name}")
            except OSError as e:
                messagebox.showerror("Error", f"Could not create file: {e}", parent=self)

    def _new_folder(self):
        """Creates a new folder in the selected directory or project root."""
        path = self._get_selected_path()
        if path and os.path.isfile(path):
            target_dir = os.path.dirname(path)
        elif path and os.path.isdir(path):
            target_dir = path
        else:
            target_dir = self.project_path

        folder_name = simpledialog.askstring("New Folder", "Enter name for the new folder:", parent=self)
        if folder_name and folder_name.strip():
            new_path = os.path.join(target_dir, folder_name)
            if os.path.exists(new_path):
                messagebox.showwarning("Exists", "A folder with that name already exists.", parent=self)
                return
            try:
                os.makedirs(new_path)
                self.refresh_file_tree()
                self.update_status(f"Created folder: {folder_name}")
            except OSError as e:
                messagebox.showerror("Error", f"Could not create folder: {e}", parent=self)

    def _populate_tree(self, parent_node="", path=None):
        """Recursively populate the file tree."""
        if path is None:
            path = self.project_path

        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            is_dir = os.path.isdir(full_path)
            # Insert node and get its ID, storing full_path in values
            node_id = self.tree.insert(parent_node, 'end', text=item, open=False, values=[full_path])
            if is_dir:
                # If it's a directory, add a placeholder child to show the expander icon
                self.tree.insert(node_id, 'end')
                # And recursively populate it
                self._populate_tree(node_id, full_path)

    def _on_tree_select(self, event):
        """Handles selection of an item in the file tree."""
        selected_ids = self.tree.selection()
        if not selected_ids:
            return

        selected_item_id = selected_ids[0]
        # Retrieve the full path stored in the 'values' tuple
        file_path = self.tree.item(selected_item_id, 'values')[0]

        if os.path.isfile(file_path):
            self.notebook.select(self.tab_frames["Edit"])
            self.update_status(f"Opened: {os.path.basename(file_path)}")
            self.edit_tab.load_file(file_path)

    def _apply_colors(self):
        """Apply theme colors to non-ttk widgets."""
        self.config(bg=self.colors['bg'])
        if self.status_bar_label:
            status_frame = self.status_bar_label.master
            status_frame.config(bg=self.colors['bg'])
            self.status_bar_label.config(bg=self.colors['bg'], fg=self.colors['quote'])

    def update_status(self, message, clear_after_ms=5000):
        """Updates the status bar message, optionally clearing it after a delay."""
        self.status_bar_label.config(text=message)
        if clear_after_ms:
            self.after(clear_after_ms, lambda: self.status_bar_label.config(text="Ready."))

    def debug_print(self, message):
        """Prints a message to the console only if debug info is enabled."""
        if self.app_config.get('developer_debug_info', False):
            print(f"[DEBUG] {message}")

    def _clear_tree(self):
        """Deletes all items from the treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def refresh_file_tree(self):
        """Clears and re-populates the file tree."""
        self._clear_tree()
        self._populate_tree()
        self.update_status("File tree refreshed.")

    def save_readme(self, content):
        """Saves the README.md file and refreshes the UI."""
        readme_path = os.path.join(self.project_path, "README.md")
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.update_status("README.md saved successfully.")
            self.refresh_file_tree()
            # Open the new file in the editor for immediate viewing
            self.notebook.select(self.tab_frames["Edit"])
            self.edit_tab.load_file_content(content, file_path=readme_path)
        except IOError as e:
            print(f"Error saving README.md: {e}")

    def save_roadmap(self, content):
        """Saves the roadmap.md file and refreshes the UI."""
        roadmap_path = os.path.join(self.project_path, "roadmap.md")
        try:
            with open(roadmap_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.update_status("roadmap.md saved successfully.")
            self.refresh_file_tree()
            # Refresh the tasks tab if it exists to show the new roadmap
            if self.tasks_tab:
                self.tasks_tab.load_and_display_roadmap()
            # Open the new file in the editor for immediate viewing
            self.notebook.select(self.tab_frames["Edit"])
            self.edit_tab.load_file_content(content, file_path=roadmap_path)
        except IOError as e:
            print(f"Error saving roadmap.md: {e}")

    def create_and_open_file(self, file_name, content=""):
        """Creates a new file in the project root and opens it in the editor."""
        new_path = os.path.join(self.project_path, file_name)
        
        if os.path.exists(new_path):
            self.update_status(f"'{file_name}' already exists, opening it.")
        else:
            try:
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status(f"Created and opened '{file_name}'")
                self.refresh_file_tree()
            except OSError as e:
                messagebox.showerror("Error", f"Could not create file: {e}", parent=self)
                return

        # Open the file in the editor
        self.notebook.select(self.tab_frames["Edit"])
        self.edit_tab.load_file(new_path)

    def save_settings(self):
        """Gathers settings from tabs and saves them to the config file."""
        if self.settings_tab:
            settings_data = self.settings_tab.get_settings_data()
            
            # Handle API key separately to save to .env
            new_api_key = settings_data.pop('gemini_api_key', None)
            if new_api_key is not None: # A value of None means "no change"
                config_manager.save_gemini_key(new_api_key)

            # If a user is logged in, their tier is managed by their session.
            # Do not save the tier from the (disabled) combobox.
            if self.current_user:
                if 'active_tier' in settings_data:
                    del settings_data['active_tier']

            # Save the rest of the settings to the JSON config file
            self.app_config.update(settings_data)
            config_manager.save_config(self.app_config)

            # If logged out, the active tier is whatever was just saved in the config.
            if not self.current_user:
                self.active_tier_name = self.app_config.get('active_tier', subscription.SubscriptionTier.FREE.value)
                self.active_tier = subscription.get_tier_by_name(self.active_tier_name)
            
            self.update_status("Settings saved.")

    def show_login_window(self):
        """Opens the modal login window."""
        from .ui.login_window import LoginWindow # Local import to avoid circular dependency
        LoginWindow(self, on_success_callback=self._handle_login_success)

    def update_all_auth_dependent_ui(self):
        """Refreshes UI elements across all tabs that depend on the active tier."""
        self._update_auth_ui() # This already handles Genesis and Settings tabs
        if self.tasks_tab:
            # This will re-render the tasks, checking permissions for buttons again
            self.tasks_tab.load_and_display_roadmap()
        # Add other tabs here if they have tier-dependent UI

    def _update_auth_ui(self):
        """Central method to update all UI components based on auth status."""
        # Update the settings tab (login button, status label, etc.)
        if self.settings_tab:
            self.settings_tab.update_auth_status()

        # A logged-out user (default profile) has restricted access.
        # The Genesis tab is for project creation and requires a user session.
        if self.current_user:
            self.notebook.tab(self.tab_frames["Genesis"], state="normal")
        else:
            self.notebook.tab(self.tab_frames["Genesis"], state="disabled")

    def _handle_login_success(self, user: auth.User):
        """Callback function for when a user successfully logs in."""
        self.current_user = user
        self.active_tier = user.tier
        self.update_status(f"Welcome, {user.email}!")
        self._update_auth_ui()

    def logout(self):
        """Logs the current user out and reverts to the default FREE tier."""
        # If the currently selected tab is the one we're about to disable,
        # switch to a different tab first.
        if self.notebook.select() == self.tab_frames["Genesis"]:
            self.notebook.select(self.tab_frames["Edit"])

        self.current_user = None
        # When logging out, always revert to the default FREE tier.
        self.active_tier = subscription.SubscriptionTier.FREE
        self.active_tier_name = self.active_tier.value
        self.update_status("Successfully logged out.")
        self._update_auth_ui()

    def on_close(self):
        """Handles window close event, saves settings, and exits the app."""
        self.save_settings()
        self.master.destroy()

    def execute_code_generation_for_task(self, task_text: str):
        """Switches to the Edit tab and executes the AI suggestion flow for a given task."""
        if self.edit_tab:
            self.notebook.select(self.tab_frames["Edit"])
            self.edit_tab.execute_ai_suggestion(task_text)
            self.update_status(f"Ready to generate code for: '{task_text[:40]}...'")

    def mark_task_as_complete(self, task_text: str):
        """Tells the Tasks tab to mark a specific task as complete."""
        if self.tasks_tab:
            self.tasks_tab.complete_task_by_text(task_text)
            self.update_status(f"Task completed: '{task_text[:40]}...'")

    def switch_theme(self, theme_name):
        """Public method to allow theme switching from outside."""
        self.theme_name = theme_name

        # Persist the theme change
        self.app_config['theme'] = theme_name
        config_manager.save_config(self.app_config)

        self.colors = theme.get_theme(self.theme_name)
        self._configure_styles()
        self._apply_colors()
        # Re-color tab frames and labels
        for name, frame in self.tab_frames.items():
            frame.config(bg=self.colors['bg'])
            if name == "Edit":
                if self.edit_tab:
                    self.edit_tab.apply_colors(self.colors)
            elif name == "Settings":
                if self.settings_tab:
                    self.settings_tab.apply_colors(self.colors)
            elif name == "Genesis":
                if self.genesis_tab:
                    self.genesis_tab.apply_colors(self.colors)
            elif name == "Tasks":
                if self.tasks_tab:
                    self.tasks_tab.apply_colors(self.colors)
            else:
                # Handle placeholder labels in other tabs
                for child in frame.winfo_children():
                    child.config(bg=self.colors['bg'], fg=self.colors['fg'])
