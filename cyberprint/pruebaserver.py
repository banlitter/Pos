# cyberprint_cliente.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
import socket
import threading

class ClienteCyberprint:
    def __init__(self, master):
        self.master = master
        self.master.title("CYBERPRINT Cliente")
        self.master.geometry("600x400")
        self.master.configure(bg='#1E1E1E')

        # Configuración del servidor
        self.servidor_host = "192.168.1.101"  # Cambia por la IP del servidor
        self.servidor_puerto = 9100
        self.cliente_socket = None

        # Configurar la interfaz
        self.configurar_interfaz()

    def configurar_interfaz(self):
        # Marco principal
        marco_principal = tk.Frame(self.master, bg='#1E1E1E')
        marco_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Campo de entrada para la IP del servidor
        marco_ip = tk.Frame(marco_principal, bg='#1E1E1E')
        marco_ip.pack(fill=tk.X, pady=(0, 10))

        tk.Label(marco_ip, text="IP del Servidor:", bg='#1E1E1E', fg='#CCCCCC', font=('Consolas', 10)).pack(side=tk.LEFT, padx=5)
        self.entrada_ip = tk.Entry(marco_ip, width=20, font=('Consolas', 10))
        self.entrada_ip.pack(side=tk.LEFT, padx=5)
        self.entrada_ip.insert(0, self.servidor_host)

        # Campo de entrada para el puerto del servidor
        tk.Label(marco_ip, text="Puerto:", bg='#1E1E1E', fg='#CCCCCC', font=('Consolas', 10)).pack(side=tk.LEFT, padx=5)
        self.entrada_puerto = tk.Entry(marco_ip, width=10, font=('Consolas', 10))
        self.entrada_puerto.pack(side=tk.LEFT, padx=5)
        self.entrada_puerto.insert(0, str(self.servidor_puerto))

        # Botón para conectar al servidor
        btn_conectar = tk.Button(marco_ip, text="Conectar", command=self.conectar_al_servidor, bg='#4CAF50', fg='#FFFFFF', font=('Consolas', 10), padx=10, pady=5)
        btn_conectar.pack(side=tk.LEFT, padx=5)

        # Botón para prueba de impresión y corte
        btn_prueba = tk.Button(marco_ip, text="Prueba Impresión y Corte", command=self.prueba_impresion_corte, bg='#FF9800', fg='#FFFFFF', font=('Consolas', 10), padx=10, pady=5)
        btn_prueba.pack(side=tk.LEFT, padx=5)

        # Consola de salida
        self.terminal = scrolledtext.ScrolledText(marco_principal, bg='#1E1E1E', fg='#CCCCCC', font=('Consolas', 10), wrap=tk.WORD)
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Campo de entrada para enviar comandos
        marco_comando = tk.Frame(marco_principal, bg='#1E1E1E')
        marco_comando.pack(fill=tk.X, pady=(10, 0))

        tk.Label(marco_comando, text="Comando:", bg='#1E1E1E', fg='#CCCCCC', font=('Consolas', 10)).pack(side=tk.LEFT, padx=5)
        self.entrada_comando = tk.Entry(marco_comando, width=30, font=('Consolas', 10))
        self.entrada_comando.pack(side=tk.LEFT, padx=5)

        btn_enviar = tk.Button(marco_comando, text="Enviar", command=self.enviar_comando, bg='#2196F3', fg='#FFFFFF', font=('Consolas', 10), padx=10, pady=5)
        btn_enviar.pack(side=tk.LEFT, padx=5)

    def conectar_al_servidor(self):
        """Conecta al servidor."""
        try:
            self.servidor_host = self.entrada_ip.get()
            self.servidor_puerto = int(self.entrada_puerto.get())

            self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente_socket.connect((self.servidor_host, self.servidor_puerto))
            self.terminal.insert(tk.END, f"[✔] Conectado al servidor {self.servidor_host}:{self.servidor_puerto}\n")
            threading.Thread(target=self.recibir_mensajes, daemon=True).start()
        except Exception as e:
            self.terminal.insert(tk.END, f"[X] Error al conectar al servidor: {str(e)}\n")

    def recibir_mensajes(self):
        """Recibe mensajes del servidor."""
        while True:
            try:
                mensaje = self.cliente_socket.recv(1024).decode('utf-8')
                if not mensaje:
                    break
                self.terminal.insert(tk.END, f"[Servidor] {mensaje}\n")
            except Exception as e:
                self.terminal.insert(tk.END, f"[X] Error al recibir mensaje: {str(e)}\n")
                break

    def enviar_comando(self):
        """Envía un comando al servidor."""
        try:
            comando = self.entrada_comando.get()
            if comando:
                self.cliente_socket.send(comando.encode('utf-8'))
                self.terminal.insert(tk.END, f"[✔] Comando enviado: {comando}\n")
                self.entrada_comando.delete(0, tk.END)
        except Exception as e:
            self.terminal.insert(tk.END, f"[X] Error al enviar comando: {str(e)}\n")

    def prueba_impresion_corte(self):
        """Envía comandos para realizar una prueba de impresión y corte."""
        try:
            if not self.cliente_socket:
                self.terminal.insert(tk.END, "[X] No estás conectado al servidor.\n")
                return

            # Comando para inicializar la impresora (ESC/POS)
            comando_inicializacion = b'\x1B\x40'
            self.cliente_socket.send(comando_inicializacion)

            # Comando para imprimir un texto de prueba
            texto_prueba = "Prueba de impresión desde CYBERPRINT Cliente\n"
            self.cliente_socket.send(texto_prueba.encode('utf-8'))
            self.terminal.insert(tk.END, "[✔] Comando de impresión enviado.\n")

            # Comando para cortar el papel (ESC/POS)
            comando_corte = b'\x1D\x56\x00'  # Corte completo
            self.cliente_socket.send(comando_corte)
            self.terminal.insert(tk.END, "[✔] Comando de corte enviado.\n")
        except Exception as e:
            self.terminal.insert(tk.END, f"[X] Error en la prueba de impresión y corte: {str(e)}\n")

    def on_close(self):
        """Maneja el cierre de la aplicación."""
        if messagebox.askyesno("Cerrar", "¿Deseas cerrar la aplicación?"):
            if self.cliente_socket:
                self.cliente_socket.close()
            self.master.destroy()


if __name__ == "__main__":
    raiz = tk.Tk()
    app = ClienteCyberprint(raiz)
    raiz.protocol("WM_DELETE_WINDOW", app.on_close)
    raiz.mainloop()