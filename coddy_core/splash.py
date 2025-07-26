import tkinter as tk
from . import utils

class SplashScreen(tk.Toplevel):
    """
    A splash screen window shown during application initialization.
    It attempts to load 'assets/splash.png', falling back to a
    themed text-based screen if the image is not found.
    """
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.overrideredirect(True)  # Frameless window

        try:
            # Attempt to load a splash image.
            # This requires an 'assets/splash.png' file to be bundled.
            splash_image_path = utils.resource_path("assets/splash.png")
            self.splash_image = tk.PhotoImage(file=splash_image_path)

            width = self.splash_image.width()
            height = self.splash_image.height()

            # Center the window
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            self.geometry(f'{width}x{height}+{x}+{y}')

            tk.Label(self, image=self.splash_image, borderwidth=0).pack()

        except (tk.TclError, FileNotFoundError):
            # Fallback to a text-based splash screen if image is missing
            width, height = 450, 250
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            self.geometry(f'{width}x{height}+{x}+{y}')
            self.config(bg="#1e1e1e") # Dark background

            tk.Label(self, text="Coddy V3", font=("Courier New", 24, "bold"), fg="#00ff00", bg="#1e1e1e").pack(pady=(50, 10))
            tk.Label(self, text="Initializing the forge...", font=("Courier New", 12, "italic"), fg="#a0a0a0", bg="#1e1e1e").pack(pady=5)
            tk.Label(self, text="Waking the engine...", font=("Courier New", 10), fg="#808080", bg="#1e1e1e").pack(side="bottom", pady=20)

        self.lift()
        self.update()

    def close(self):
        """Closes and destroys the splash screen window."""
        self.destroy()