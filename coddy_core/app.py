import tkinter as tk
from landing_page import CoddyLandingPage
from main_application import MainApplication

class App:
    """
    The main application controller. Manages window flow and lifecycle.
    """
    def __init__(self):
        # The root Tk instance is created but immediately hidden.
        # It serves as the parent for all other windows and manages the mainloop.
        self.root = tk.Tk()
        self.root.withdraw()

        self.landing_page = None
        self.main_app_window = None
        self.current_theme = 'dark' # Default theme

    def start(self):
        """Starts the application by showing the landing page."""
        self.show_landing_page()
        self.root.mainloop()

    def show_landing_page(self):
        """Creates and displays the landing page window."""
        self.landing_page = CoddyLandingPage(
            master=self.root,
            theme_name=self.current_theme,
            on_project_selected=self.launch_main_app,
            on_theme_switched=self.on_theme_switched
        )
        # If the landing page is closed, the whole app should exit.
        self.landing_page.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def on_theme_switched(self, theme_name):
        """Callback for when the theme is changed on the landing page."""
        self.current_theme = theme_name
        # If the main app is already open, switch its theme too.
        if self.main_app_window and self.main_app_window.winfo_exists():
            self.main_app_window.switch_theme(theme_name)

    def launch_main_app(self, project_path):
        """Hides the landing page and opens the main application window."""
        if self.landing_page:
            self.landing_page.destroy() # Close the landing page

        self.main_app_window = MainApplication(
            master=self.root, project_path=project_path, theme_name=self.current_theme
        )
        self.main_app_window.protocol("WM_DELETE_WINDOW", self.on_app_close)

    def on_app_close(self):
        """Handles the main application window closing event."""
        if self.main_app_window and self.main_app_window.winfo_exists():
            self.main_app_window.save_settings()
        self.root.destroy()

if __name__ == "__main__":
    app = App()
    app.start()