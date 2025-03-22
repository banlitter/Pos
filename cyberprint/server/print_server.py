import socket
import threading
import win32print
from enum import Enum
from utils.logger import Logger

class TipoDeMensaje(Enum):
    INFO = "información"
    EXITO = "éxito"
    ERROR = "error"
    ADVERTENCIA = "advertencia"
    CONEXION = "conexión"
    SISTEMA = "sistema"

class ServidorDeImpresion:
    def __init__(self, callback_log, host='0.0.0.0', puerto=9100):
        self.host = host
        self.puerto = puerto
        self.socket_servidor = None
        self.ejecutando = False
        self.log = callback_log
        self.nombre_impresora = None

    def establecer_impresora(self, nombre_impresora):
        self.nombre_impresora = nombre_impresora

    def iniciar_servidor(self):
        try:
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_servidor.bind((self.host, self.puerto))
            self.socket_servidor.listen(5)
            self.ejecutando = True
            self.log(f"[!] SERVIDOR INICIALIZADO [!]\n■ IP: {self.host}\n■ PUERTO: {self.puerto}\n■ IMPRESORA DESTINO: {self.nombre_impresora}", TipoDeMensaje.SISTEMA)
            threading.Thread(target=self.aceptar_conexiones, daemon=True).start()
            return True
        except Exception as e:
            self.log(f"[X] ERROR AL INICIAR EL SERVIDOR: {str(e)}", TipoDeMensaje.ERROR)
            return False

    def aceptar_conexiones(self):
        while self.ejecutando and self.socket_servidor:
            try:
                cliente_socket, addr = self.socket_servidor.accept()
                self.log(f"[+] CONEXIÓN ENTRANTE:\n■ IP: {addr[0]}\n■ PUERTO: {addr[1]}\n■ IMPRESORA: {self.nombre_impresora}", TipoDeMensaje.CONEXION)
                threading.Thread(target=self.manejar_cliente, args=(cliente_socket,), daemon=True).start()
            except Exception as e:
                if self.ejecutando:
                    self.log(f"[!] ERROR EN CONEXIÓN: {str(e)}", TipoDeMensaje.ADVERTENCIA)

    def manejar_cliente(self, cliente_socket):
        try:
            datos = b''
            while True:
                fragmento = cliente_socket.recv(4096)
                if not fragmento: break
                datos += fragmento
                self.log(f"[•] FLUJO DE DATOS: {len(datos)} bytes", TipoDeMensaje.INFO)
            
            if datos and self.nombre_impresora:
                self.enviar_a_impresora(datos)
                self.log("[✔] TRABAJO DE IMPRESIÓN EJECUTADO", TipoDeMensaje.EXITO)
        except Exception as e:
            self.log(f"[X] ERROR EN EL PROCESO DE DATOS: {str(e)}", TipoDeMensaje.ERROR)
        finally:
            cliente_socket.close()

    def enviar_a_impresora(self, datos):
        h_impresora = None
        try:
            h_impresora = win32print.OpenPrinter(self.nombre_impresora)
            doc_info = ("IMPRESION_HACKER", None, "RAW")
            win32print.StartDocPrinter(h_impresora, 1, doc_info)
            win32print.StartPagePrinter(h_impresora)
            win32print.WritePrinter(h_impresora, datos)
            self.log(f"[•] IMPRIMIENDO EN: {self.nombre_impresora}", TipoDeMensaje.INFO)
        except Exception as e:
            self.log(f"[X] ERROR AL IMPRIMIR: {str(e)}", TipoDeMensaje.ERROR)
            if h_impresora: 
                win32print.AbortPrinter(h_impresora)
        finally:
            if h_impresora:
                win32print.EndPagePrinter(h_impresora)
                win32print.EndDocPrinter(h_impresora)
                win32print.ClosePrinter(h_impresora)

    def detener_servidor(self):
        if self.ejecutando:
            self.ejecutando = False
            try:
                if self.socket_servidor:
                    self.socket_servidor.close()
                    self.socket_servidor = None
                    self.log("[!] SERVIDOR DETENIDO COMPLETAMENTE", TipoDeMensaje.ADVERTENCIA)
            except Exception as e:
                self.log(f"[!] ERROR AL DETENER EL SERVIDOR: {str(e)}", TipoDeMensaje.ADVERTENCIA)