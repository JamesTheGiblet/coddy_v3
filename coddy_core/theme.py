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
    },
    'light': {
        'bg': '#f5f5f5',
        'fg': '#212121',
        'accent': '#005cb2',
        'accent_active': '#003681',
        'accent_hover': '#006dcc',
        'quote': '#616161',
        'button_fg': '#ffffff',
    },
    'weird': {
        'bg': '#1a001a',          # Dark purple
        'fg': '#e0e0e0',          # Light grey
        'accent': '#ff00ff',      # Neon magenta/pink
        'accent_active': '#cc00cc',# Darker magenta
        'accent_hover': '#ff33ff', # Lighter magenta
        'quote': '#00ffff',        # Neon cyan
        'button_fg': '#000000',   # Black text on bright button
    },
}

def get_theme(name='dark'):
    """Returns the color dictionary for a given theme name."""
    return THEMES.get(name, THEMES['dark'])

def get_theme_names():
    """Returns a list of available theme names."""
    return list(THEMES.keys())