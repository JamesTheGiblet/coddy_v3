import tkinter as tk
from .landing_page import LandingPage
from . import database

class App:
    """
    The main application controller. Manages window flow and lifecycle.
    """
    def __init__(self):
        database.init_db() # Initialize the database on startup
        self.root = tk.Tk()
        self.root.withdraw() # Hide the root window, it only serves as a parent

    def start(self):
        """Starts the application by showing the landing page."""
        LandingPage(master=self.root)
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()