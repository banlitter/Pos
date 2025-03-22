import serial.tools.list_ports
import win32print

def escanear_dispositivos():
    dispositivos = []
    try:
        # Escanear puertos COM
        for puerto in serial.tools.list_ports.comports():
            dispositivos.append(f"COM::{puerto.device} - {puerto.description}")
        
        # Escanear impresoras
        impresoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        for impresora in impresoras:
            dispositivos.append(f"IMPRESORA::{impresora[2]}")

        return dispositivos
    except Exception as e:
        raise Exception(f"Error en el escaneo: {str(e)}")