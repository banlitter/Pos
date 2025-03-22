import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import threading
import serial
from scapy.all import ARP, Ether, srp
import socket
from server.print_server import ServidorDeImpresion, TipoDeMensaje
from utils.device_scanner import escanear_dispositivos
from config.settings import Config

class TerminalCibernetica:
    def __init__(self, master):
        self.master = master
        self.master.title("CYBERPRINT v2.0")
        self.master.geometry("900x650")
        self.master.configure(bg='#263238')  # Fondo oscuro con color sutil
        self.ejecutando = True

        # Fuente y colores
        self.fuente = ('Consolas', 10)
        self.colores = {
            'fondo': '#263238',  # Fondo más suave y oscuro
            'terminal': '#ECEFF1',  # Texto más claro
            'boton': '#607D8B',  # Color moderno para los botones
            'texto_boton': '#FFFFFF',
            'barra_estado': '#455A64',  # Color suave para la barra de estado
            'hover': '#90A4AE'  # Efecto hover en los botones
        }

        # Configuración del servidor
        self.servidor_impresion = ServidorDeImpresion(self.registro_terminal, Config.HOST, Config.PUERTO)

        # Configurar la interfaz
        self.configurar_interfaz()

    def configurar_interfaz(self):
        # Marco principal
        marco_principal = tk.Frame(self.master, bg=self.colores['fondo'])
        marco_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Marco de botones (parte superior)
        marco_botones = tk.Frame(marco_principal, bg=self.colores['fondo'])
        marco_botones.pack(fill=tk.X, pady=(0, 15))

        # Botones de comandos con iconos y efecto hover
        botones = [
            ('INICIAR SERVIDOR', self.toggle_servidor, 'server', "Inicia o detiene el servidor de impresión"),
            ('ESCANEAR DISPOSITIVOS', self.escanear_dispositivos, 'scan', "Escanea dispositivos conectados"),
            ('ESCANEAR IP', self.escanear_ip_automatico, 'ip', "Escanea la red local para detectar dispositivos activos"),
            ('ABRIR CAJÓN', self.abrir_cajon, 'drawer', "Envía comando para abrir el cajón de la impresora"),
            ('CORTAR PAPEL', self.cortar_papel, 'cut', "Envía comando para cortar el papel"),
            ('EXPORTAR REGISTROS', self.exportar_registros, 'export', "Exporta los registros a un archivo de texto")
        ]

        for texto, comando, icono, tooltip in botones:
            btn = tk.Button(marco_botones,
                            text=texto,
                            command=comando,
                            bg=self.colores['boton'],
                            fg=self.colores['texto_boton'],
                            activebackground=self.colores['hover'],
                            activeforeground=self.colores['texto_boton'],
                            borderwidth=0,
                            font=self.fuente,
                            padx=10,
                            pady=8,
                            relief='flat')
            btn.pack(side=tk.LEFT, padx=10)
            self.agregar_tooltip(btn, tooltip)

        # Selector de impresoras
        self.variable_impresora = tk.StringVar()
        self.selector_impresoras = ttk.Combobox(marco_botones,
                                                textvariable=self.variable_impresora,
                                                state='readonly',
                                                width=30,
                                                font=self.fuente)
        self.selector_impresoras.pack(side=tk.LEFT, padx=10)

        # Consola de salida
        self.terminal = scrolledtext.ScrolledText(marco_principal,
                                                 bg=self.colores['fondo'],
                                                 fg=self.colores['terminal'],
                                                 insertbackground=self.colores['terminal'],
                                                 font=self.fuente,
                                                 wrap=tk.WORD,
                                                 bd=0,
                                                 relief='flat',
                                                 highlightthickness=0)
        self.terminal.pack(fill=tk.BOTH, expand=True)

        # Barra de estado
        self.barra_estado = tk.Label(marco_principal,
                                     text="Listo",
                                     bg=self.colores['barra_estado'],
                                     fg=self.colores['terminal'],
                                     font=self.fuente,
                                     anchor=tk.W, padx=10)
        self.barra_estado.pack(fill=tk.X, pady=(5, 0))

    def agregar_tooltip(self, widget, texto):
        """Agrega un tooltip a un widget."""
        tooltip = ttk.Label(self.master, text=texto, background="#FFFFE0", relief="solid", borderwidth=1, font=self.fuente)
        def mostrar_tooltip(event):
            tooltip.place(x=event.x_root + 10, y=event.y_root + 10)
        def ocultar_tooltip(event):
            tooltip.place_forget()
        widget.bind("<Enter>", mostrar_tooltip)
        widget.bind("<Leave>", ocultar_tooltip)

    def registro_terminal(self, mensaje, tipo_mensaje=TipoDeMensaje.INFO):
        """Registra mensajes en la terminal con resaltado de sintaxis."""
        self.terminal.configure(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        tag = str(tipo_mensaje).lower()
        self.terminal.insert('end', f"[{timestamp}] {mensaje}\n", tag)
        self.terminal.tag_config('info', foreground='#ECEFF1')  # Gris claro
        self.terminal.tag_config('error', foreground='#FF5252')  # Rojo brillante
        self.terminal.tag_config('exito', foreground='#66BB6A')  # Verde brillante
        self.terminal.tag_config('advertencia', foreground='#FFA726')  # Naranja brillante
        self.terminal.tag_config('sistema', foreground='#42A5F5')  # Azul brillante
        self.terminal.see('end')
        self.terminal.configure(state='disabled')

    def escanear_dispositivos(self):
        """Escanea dispositivos disponibles."""
        def tarea_escanear():
            dispositivos = escanear_dispositivos()
            self.master.after(0, lambda: self.actualizar_lista_dispositivos(dispositivos))

        threading.Thread(target=tarea_escanear, daemon=True).start()

    def actualizar_lista_dispositivos(self, dispositivos):
        """Actualiza la lista de dispositivos.""" 
        if dispositivos:
            self.registro_terminal("[✔] Dispositivos detectados:", TipoDeMensaje.EXITO)
            for dispositivo in dispositivos:
                self.registro_terminal(f"  - {dispositivo}", TipoDeMensaje.INFO)
            self.selector_impresoras['values'] = dispositivos
            if not self.variable_impresora.get():
                self.variable_impresora.set(dispositivos[0])
        else:
            self.registro_terminal("[X] No se detectaron dispositivos.", TipoDeMensaje.ERROR)

    def escanear_ip_automatico(self):
        """Escanea la red local para detectar dispositivos activos."""
        def tarea_escanear():
            try:
                # Obtener la dirección IP de la red local
                hostname = socket.gethostname()
                ip_local = socket.gethostbyname(hostname)
                red = ".".join(ip_local.split(".")[:-1]) + ".0/24"  # Escanear toda la subred

                # Crear paquete ARP
                arp = ARP(pdst=red)
                ether = Ether(dst="ff:ff:ff:ff:ff:ff")
                paquete = ether / arp

                # Enviar y recibir paquetes
                resultado = srp(paquete, timeout=2, verbose=0)[0]

                # Procesar resultados
                dispositivos = []
                for enviado, recibido in resultado:
                    dispositivos.append({'ip': recibido.psrc, 'mac': recibido.hwsrc})

                # Actualizar la interfaz
                self.master.after(0, lambda: self.mostrar_dispositivos_red(dispositivos))
            except Exception as e:
                self.master.after(0, lambda: self.registro_terminal(f"[X] Error al escanear la red: {str(e)}", TipoDeMensaje.ERROR))

        # Ejecutar en un hilo separado
        threading.Thread(target=tarea_escanear, daemon=True).start()

    def mostrar_dispositivos_red(self, dispositivos):
        """Muestra los dispositivos detectados en la red.""" 
        if dispositivos:
            self.registro_terminal("[✔] Dispositivos detectados en la red:", TipoDeMensaje.EXITO)
            for dispositivo in dispositivos:
                self.registro_terminal(f"  - IP: {dispositivo['ip']}, MAC: {dispositivo['mac']}", TipoDeMensaje.INFO)
        else:
            self.registro_terminal("[X] No se detectaron dispositivos en la red.", TipoDeMensaje.ERROR)

    def toggle_servidor(self):
        """Inicia o detiene el servidor."""
        if not self.servidor_impresion.ejecutando:
            if self.servidor_impresion.iniciar_servidor():
                self.registro_terminal("[!] Servidor activado.", TipoDeMensaje.SISTEMA)
                self.barra_estado.config(text="Servidor activado")
            else:
                self.registro_terminal("[X] Error al activar el servidor.", TipoDeMensaje.ERROR)
                self.barra_estado.config(text="Error al activar el servidor")
        else:
            self.servidor_impresion.detener_servidor()
            self.registro_terminal("[!] Servidor desactivado.", TipoDeMensaje.ADVERTENCIA)
            self.barra_estado.config(text="Servidor desactivado")

    def abrir_cajon(self):
        """Envía el comando para abrir el cajón."""
        self.enviar_comando([b'\x1B\x70\x00\x19\xFA'])
        self.registro_terminal("[•] Comando de cajón enviado.", TipoDeMensaje.INFO)

    def cortar_papel(self):
        """Envía el comando para cortar el papel."""
        self.enviar_comando([b'\x1D\x56\x00'])
        self.registro_terminal("[•] Comando de corte enviado.", TipoDeMensaje.INFO)

    def enviar_comando(self, comando):
        """Envía comandos al dispositivo seleccionado."""
        seleccionado = self.variable_impresora.get()
        if not seleccionado:
            self.registro_terminal("[X] No se seleccionó ninguna impresora.", TipoDeMensaje.ERROR)
            return
        
        try:
            if seleccionado.startswith("IMPRESORA::"):
                nombre_impresora = seleccionado.split("::")[1].strip()
                if self.servidor_impresion.nombre_impresora != nombre_impresora:
                    self.servidor_impresion.establecer_impresora(nombre_impresora)
                self.servidor_impresion.enviar_a_impresora(comando[0])
                self.registro_terminal(f"[✔] Comando enviado a {nombre_impresora}.", TipoDeMensaje.EXITO)
            else:
                puerto = seleccionado.split("::")[1].split("-")[0].strip()
                with serial.Serial(puerto, 9600, timeout=1) as ser:
                    ser.write(comando[0])
                self.registro_terminal(f"[✔] Comando enviado al puerto: {puerto}", TipoDeMensaje.EXITO)
        except serial.SerialException as se:
            self.registro_terminal(f"[X] Error serial: {str(se)}", TipoDeMensaje.ERROR)
        except Exception as e:
            self.registro_terminal(f"[X] Error de comando: {str(e)}", TipoDeMensaje.ERROR)

    def exportar_registros(self):
        """Exporta los registros a un archivo."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"registros_cyber_{timestamp}.txt"
            with open(nombre_archivo, 'w') as f:
                f.write(self.terminal.get('1.0', tk.END))
            self.registro_terminal(f"[✔] Registros exportados: {nombre_archivo}", TipoDeMensaje.EXITO)
        except Exception as e:
            self.registro_terminal(f"[X] Error al exportar: {str(e)}", TipoDeMensaje.ERROR)

    def on_close(self):
        """Maneja el cierre de la aplicación.""" 
        if messagebox.askyesno("Cerrar", "¿Deseas cerrar la aplicación?"):
            self.ejecutando = False
            self.servidor_impresion.detener_servidor()
            self.master.quit()  # Mejor usar quit() para detener la aplicación

if __name__ == "__main__":
    raiz = tk.Tk()
    app = TerminalCibernetica(raiz)
    raiz.protocol("WM_DELETE_WINDOW", app.on_close)
    raiz.mainloop()
