import tkinter as tk
import os
import logging
from tklinenums import TkLineNumbers
from pygments import lex
from pygments.lexers import get_lexer_by_name

# Set up logging
LOG_DIR = r"C:\Users\gilbe\Documents\GitHub\coddy_v3\coddy_core\log"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "code_editor.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

class CodeEditor(tk.Frame):
    """
    A custom code editor widget that includes line numbers and syntax highlighting.
    """
    def __init__(self, master, colors, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colors = colors
        self._highlight_job = None

        # The core text widget
        self.text = tk.Text(self, wrap=tk.WORD, relief=tk.FLAT, borderwidth=0, undo=True)
        
        # The line numbers bar
        self.linenumbers = TkLineNumbers(self, self.text, justify="right")

        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        # Get the Python lexer for highlighting
        self.lexer = get_lexer_by_name("python")

        # Configure the initial theme
        self.apply_colors(self.colors)

        # Bind events
        self.text.bind("<<Modified>>", self._on_text_modified, add=True)
        self.text.bind("<KeyRelease>", self.trigger_highlight, add=True)
        logger.info("CodeEditor initialized.")

    def _on_text_modified(self, event=None):
        """Handles the text modification event to redraw line numbers."""
        self.linenumbers.redraw()

    def trigger_highlight(self, event=None):
        """Schedules a syntax highlighting job to run after a short delay."""
        logger.debug("Highlight triggered.")
        if self._highlight_job:
            self.after_cancel(self._highlight_job)
        self._highlight_job = self.after(100, self._perform_highlight)

    def _perform_highlight(self):
        """Applies syntax highlighting to the text in the widget."""
        try:
            code = self.text.get("1.0", "end-1c")
            
            # Remove all previous syntax tags to prevent color buildup
            for tag in self.text.tag_names():
                if str(tag).startswith("Token."):
                    self.text.tag_remove(tag, "1.0", "end")

            # Apply new tags based on tokenization
            self.text.mark_set("range_start", "1.0")
            for token, content in lex(code, self.lexer):
                self.text.mark_set("range_end", f"range_start + {len(content)}c")
                
                # Apply the most specific tag that exists in our theme
                # This allows falling back from Token.Keyword.Constant to Token.Keyword
                current_token_type = token
                while str(current_token_type) not in self.syntax_colors and current_token_type.parent:
                    current_token_type = current_token_type.parent
                
                tag_name = str(current_token_type)
                if tag_name in self.syntax_colors:
                    self.text.tag_add(tag_name, "range_start", "range_end")
                
                self.text.mark_set("range_start", "range_end")
        except Exception as e:
            logger.exception(f"An error occurred during syntax highlighting: {e}")

    def _configure_tags(self):
        """Configures the text widget's tags with colors from the theme."""
        self.syntax_colors = self.colors.get('syntax', {})
        for token_name, color in self.syntax_colors.items():
            try:
                self.text.tag_configure(token_name, foreground=color)
            except tk.TclError as e:
                logger.warning(f"Could not configure tag '{token_name}' with color '{color}': {e}")

    def apply_colors(self, colors):
        """Applies a new color theme to the editor."""
        try:
            self.colors = colors
            self.text.config(
                bg=self.colors.get('bg', '#2b2b2b'),
                fg=self.colors.get('fg', '#dcdcdc'),
                insertbackground=self.colors.get('fg', '#dcdcdc'),
                selectbackground=self.colors.get('accent', '#007acc')
            )
            # Set colors for the line numbers canvas and text
            self.linenumbers.config(bg=self.colors.get('bg', '#2b2b2b'))
            self.linenumbers.foreground = self.colors.get('quote', '#9e9e9e')
            self.linenumbers.redraw()
            self._configure_tags()
            # Trigger a re-highlight to apply new tag colors
            self.trigger_highlight()
            logger.info("New color theme applied successfully.")
        except Exception as e:
            logger.exception(f"An error occurred applying color theme: {e}")