import socket

class Config:
    # Obtener la IP local automáticamente
    HOST = socket.gethostbyname(socket.gethostname())  # IP local
    PUERTO = 9100
    FUENTE = ('Consolas', 10)
    COLORES = {
        'fondo': '#001100',
        'terminal': '#00FF00',
        'acento': '#00FF00',
        'advertencia': '#FF0000',
        'exito': '#00FF00',
        'conexion': '#00FFFF'
    }