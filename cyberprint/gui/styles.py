# styles.py
class Theme:
    """Clase base para temas."""
    def __init__(self, background, foreground, button_color, accent_color):
        self.background = background
        self.foreground = foreground
        self.button_color = button_color
        self.accent_color = accent_color

class DarkTheme(Theme):
    def __init__(self):
        super().__init__('#263238', '#ECEFF1', '#607D8B', '#42A5F5')

class LightTheme(Theme):
    def __init__(self):
        super().__init__('#FFFFFF', '#212121', '#388E3C', '#1976D2')

class ThemeManager:
    """Clase para manejar la aplicación de temas"""
    def __init__(self, master):
        self.master = master
        self.current_theme = DarkTheme()

    def apply_theme(self, theme: Theme):
        """Aplica un tema"""
        self.current_theme = theme
        self.master.configure(bg=theme.background)
        # Aquí puedes aplicar otros cambios visuales a los componentes como botones, texto, etc.
