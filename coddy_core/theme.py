"""
Centralized theme management for the Coddy V3 application.

This module provides color palettes for different UI themes, making it easy
to switch between light, dark, or other custom themes.
"""

THEMES = {
    'dark': {
        'bg': '#2b2b2b',
        'fg': '#dcdcdc',
        'accent': '#007acc',
        'accent_active': '#005f9e',
        'accent_hover': '#008fef',
        'quote': '#9e9e9e',
        'button_fg': '#ffffff',
        'syntax': {
            'Token.Keyword': '#cc7832',
            'Token.Name.Function': '#ffc66d',
            'Token.String': '#a5c261',
            'Token.Comment': '#808080',
            'Token.Operator': '#dcdcdc',
            'Token.Number': '#6897bb',
            'Token.Punctuation': '#dcdcdc',
            'Token.Name.Class': '#a9b7c6',
        }
    },
    'light': {
        'bg': '#f5f5f5',
        'fg': '#212121',
        'accent': '#005cb2',
        'accent_active': '#003681',
        'accent_hover': '#006dcc',
        'quote': '#616161',
        'button_fg': '#ffffff',
        'syntax': {
            'Token.Keyword': '#0000ff',
            'Token.Name.Function': '#795e26',
            'Token.String': '#a31515',
            'Token.Comment': '#008000',
            'Token.Operator': '#333333',
            'Token.Number': '#098658',
            'Token.Punctuation': '#333333',
            'Token.Name.Class': '#267f99',
        }
    },
    'weird': {
        'bg': '#1a001a',          # Dark purple
        'fg': '#e0e0e0',          # Light grey
        'accent': '#ff00ff',      # Neon magenta/pink
        'accent_active': '#cc00cc',# Darker magenta
        'accent_hover': '#ff33ff', # Lighter magenta
        'quote': '#00ffff',        # Neon cyan
        'button_fg': '#000000',   # Black text on bright button
        'syntax': {
            'Token.Keyword': '#ff00ff',
            'Token.Name.Function': '#ffff00',
            'Token.String': '#00ff00',
            'Token.Comment': '#00ffff',
            'Token.Operator': '#ffffff',
            'Token.Number': '#ff9900',
            'Token.Punctuation': '#ffffff',
            'Token.Name.Class': '#ff00ff',
        }
    },
}

def get_theme(name='dark'):
    """Returns the color dictionary for a given theme name."""
    return THEMES.get(name, THEMES['dark'])

def get_theme_names():
    """Returns a list of available theme names."""
    return list(THEMES.keys())