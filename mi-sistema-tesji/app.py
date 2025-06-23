#!/usr/bin/env python3
"""
Punto de entrada alternativo para Render
"""
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación principal
from unified_server import app, main

if __name__ == "__main__":
    main()
