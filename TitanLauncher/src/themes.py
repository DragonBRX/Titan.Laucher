#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TITAN LAUNCHER - Sistema de Temas
Versão: 2.5.0
"""

THEMES = {
    "dark": {
        "name": "Dark (Padrão)",
        "bg_primary": "#1a1a1a",
        "bg_secondary": "#2b2b2b",
        "bg_tertiary": "#353535",
        "fg_primary": "#ffffff",
        "fg_secondary": "#aaaaaa",
        "accent": "#4a9eff",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "border": "#454545",
    },
    "light": {
        "name": "Light",
        "bg_primary": "#ffffff",
        "bg_secondary": "#f5f5f5",
        "bg_tertiary": "#e0e0e0",
        "fg_primary": "#000000",
        "fg_secondary": "#666666",
        "accent": "#2196f3",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "border": "#cccccc",
    },
    "nord": {
        "name": "Nord",
        "bg_primary": "#2e3440",
        "bg_secondary": "#3b4252",
        "bg_tertiary": "#434c5e",
        "fg_primary": "#eceff4",
        "fg_secondary": "#d8dee9",
        "accent": "#88c0d0",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "error": "#bf616a",
        "border": "#4c566a",
    },
    "dracula": {
        "name": "Dracula",
        "bg_primary": "#282a36",
        "bg_secondary": "#44475a",
        "bg_tertiary": "#6272a4",
        "fg_primary": "#f8f8f2",
        "fg_secondary": "#bd93f9",
        "accent": "#ff79c6",
        "success": "#50fa7b",
        "warning": "#f1fa8c",
        "error": "#ff5555",
        "border": "#6272a4",
    },
    "monokai": {
        "name": "Monokai",
        "bg_primary": "#272822",
        "bg_secondary": "#3e3d32",
        "bg_tertiary": "#49483e",
        "fg_primary": "#f8f8f2",
        "fg_secondary": "#75715e",
        "accent": "#66d9ef",
        "success": "#a6e22e",
        "warning": "#e6db74",
        "error": "#f92672",
        "border": "#49483e",
    },
    "ocean": {
        "name": "Ocean",
        "bg_primary": "#0d1117",
        "bg_secondary": "#161b22",
        "bg_tertiary": "#21262d",
        "fg_primary": "#c9d1d9",
        "fg_secondary": "#8b949e",
        "accent": "#58a6ff",
        "success": "#3fb950",
        "warning": "#d29922",
        "error": "#f85149",
        "border": "#30363d",
    },
    "gruvbox": {
        "name": "Gruvbox",
        "bg_primary": "#282828",
        "bg_secondary": "#3c3836",
        "bg_tertiary": "#504945",
        "fg_primary": "#ebdbb2",
        "fg_secondary": "#a89984",
        "accent": "#83a598",
        "success": "#b8bb26",
        "warning": "#fabd2f",
        "error": "#fb4934",
        "border": "#504945",
    },
    "solarized_dark": {
        "name": "Solarized Dark",
        "bg_primary": "#002b36",
        "bg_secondary": "#073642",
        "bg_tertiary": "#586e75",
        "fg_primary": "#fdf6e3",
        "fg_secondary": "#93a1a1",
        "accent": "#268bd2",
        "success": "#859900",
        "warning": "#b58900",
        "error": "#dc322f",
        "border": "#586e75",
    },
    "cyberpunk": {
        "name": "Cyberpunk",
        "bg_primary": "#0a0e27",
        "bg_secondary": "#1a1f3a",
        "bg_tertiary": "#2a2f4a",
        "fg_primary": "#00ffff",
        "fg_secondary": "#ff00ff",
        "accent": "#ffff00",
        "success": "#00ff00",
        "warning": "#ff9900",
        "error": "#ff0099",
        "border": "#00ffff",
    },
    "creeper": {
        "name": "Creeper",
        "bg_primary": "#0d6e0d",
        "bg_secondary": "#0f8f0f",
        "bg_tertiary": "#11a011",
        "fg_primary": "#ffffff",
        "fg_secondary": "#ccffcc",
        "accent": "#00ff00",
        "success": "#4caf50",
        "warning": "#ffeb3b",
        "error": "#000000",
        "border": "#00cc00",
    }
}


class ThemeManager:
    """Gerenciador de temas"""
    
    def __init__(self):
        self.current_theme = "dark"
        self.custom_themes = {}
    
    def get_theme(self, theme_name=None):
        """Retorna um tema"""
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name in THEMES:
            return THEMES[theme_name]
        elif theme_name in self.custom_themes:
            return self.custom_themes[theme_name]
        else:
            return THEMES["dark"]
    
    def set_theme(self, theme_name):
        """Define o tema atual"""
        if theme_name in THEMES or theme_name in self.custom_themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_all_themes(self):
        """Retorna lista de todos os temas"""
        themes = []
        for key, theme in THEMES.items():
            themes.append((key, theme["name"]))
        for key, theme in self.custom_themes.items():
            themes.append((key, theme["name"]))
        return themes
    
    def add_custom_theme(self, name, colors):
        """Adiciona um tema customizado"""
        self.custom_themes[name] = colors
    
    def get_color(self, color_name):
        """Retorna uma cor específica do tema atual"""
        theme = self.get_theme()
        return theme.get(color_name, "#ffffff")
