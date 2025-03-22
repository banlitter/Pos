import tkinter as tk
from gui.terminal_ui import TerminalCibernetica
from utils.admin_check import verificar_privilegios_admin

if __name__ == "__main__":
    verificar_privilegios_admin()
    raiz = tk.Tk()
    app = TerminalCibernetica(raiz)
    raiz.protocol("WM_DELETE_WINDOW", app.on_close)
    raiz.mainloop()