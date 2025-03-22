# test_device_scanner.py
import pytest
from utils.device_scanner import escanear_dispositivos

def test_escanear_dispositivos():
    dispositivos = escanear_dispositivos()
    assert isinstance(dispositivos, list)
    assert all(isinstance(d, str) for d in dispositivos)
