import logging

class Logger:
    def __init__(self, callback_log):
        self.callback_log = callback_log

    def log(self, mensaje, tipo_mensaje):
        self.callback_log(mensaje, tipo_mensaje)