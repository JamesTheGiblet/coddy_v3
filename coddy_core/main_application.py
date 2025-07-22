import tkinter as tk
from tkinter import ttk
import os
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
        self.active_tier_name = self.app_config.get('active_tier', subscription.SubscriptionTier.FREE.value)
        self.active_tier = subscription.get_tier_by_name(self.active_tier_name)
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
            self.edit_tab.load_file(file_path)

    def _apply_colors(self):
        """Apply theme colors to non-ttk widgets."""
        self.config(bg=self.colors['bg'])

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
        self.debug_print("File tree refreshed.")

    def save_readme(self, content):
        """Saves the README.md file and refreshes the UI."""
        readme_path = os.path.join(self.project_path, "README.md")
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.debug_print(f"README.md saved to {readme_path}")
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
            self.debug_print(f"roadmap.md saved to {roadmap_path}")
            self.refresh_file_tree()
            # Open the new file in the editor for immediate viewing
            self.notebook.select(self.tab_frames["Edit"])
            self.edit_tab.load_file_content(content, file_path=roadmap_path)
        except IOError as e:
            print(f"Error saving roadmap.md: {e}")

    def save_settings(self):
        """Gathers settings from tabs and saves them to the config file."""
        if self.settings_tab:
            settings_data = self.settings_tab.get_settings_data()
            
            # Handle API key separately to save to .env
            new_api_key = settings_data.pop('gemini_api_key', None)
            if new_api_key is not None: # A value of None means "no change"
                config_manager.save_gemini_key(new_api_key)

            # Save the rest of the settings to the JSON config file
            self.app_config.update(settings_data)
            config_manager.save_config(self.app_config)

            # Reload the active tier in the application after saving
            self.active_tier_name = self.app_config.get('active_tier', subscription.SubscriptionTier.FREE.value)
            self.active_tier = subscription.get_tier_by_name(self.active_tier_name)
            self.debug_print(f"Settings saved. Active tier is now: {self.active_tier.value}")

    def show_login_window(self):
        """Opens the modal login window."""
        from .ui.login_window import LoginWindow # Local import to avoid circular dependency
        LoginWindow(self, on_success_callback=self._handle_login_success)

    def _handle_login_success(self, user: auth.User):
        """Callback function for when a user successfully logs in."""
        self.current_user = user
        self.active_tier = user.tier
        self.debug_print(f"User {user.email} logged in. Active tier is now: {self.active_tier.value}")
        if self.settings_tab:
            self.settings_tab.update_auth_status()

    def logout(self):
        """Logs the current user out and reverts to the locally configured tier."""
        self.current_user = None
        self.active_tier = subscription.get_tier_by_name(self.app_config.get('active_tier', 'Free'))
        self.debug_print(f"User logged out. Active tier reverted to: {self.active_tier.value}")
        if self.settings_tab:
            self.settings_tab.update_auth_status()

    def on_close(self):
        """Handles window close event, saves settings, and exits the app."""
        self.save_settings()
        self.master.destroy()

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
