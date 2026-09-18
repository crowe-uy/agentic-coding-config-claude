# -*- mode: python ; coding: utf-8 -*-
"""Empaquetado del bot con PyInstaller.

Genera un .exe standalone para equipos donde el cliente no permite instalar
Python. Ver docs/empaquetado.md del plugin para el flujo completo.

Uso: pyinstaller paquete.spec
Salida: dist/paquete_bot.exe

Onefile (un solo binario, el modo de abajo): simple para entregar al
cliente, pero arranca un poco más lento y algunos antivirus corporativos
lo marcan como sospechoso por cómo empaqueta. Si eso da problemas, cambiar
a onedir (una carpeta con el .exe y sus dependencias sueltas): comentar el
bloque EXE de onefile y descomentar el bloque EXE + COLLECT de onedir, más
abajo.
"""

NOMBRE = "paquete_bot"  # Reemplazado por /nuevo-bot al crear el proyecto.

a = Analysis(
    ["ejecutar.py"],
    pathex=["src"],
    binaries=[],
    # Las parametrizaciones (datos/) y .env.example NO se empaquetan:
    # tienen que poder editarse sin reconstruir el .exe.
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# --- Onefile: un solo .exe (modo activo por defecto) ---
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=NOMBRE,
    console=True,  # bot desatendido: deja ver la salida si se corre a mano
    upx=True,
)

# --- Onedir: una carpeta con el .exe y sus dependencias (alternativa) ---
# Comentar el bloque EXE de arriba y descomentar este si onefile da
# problemas de antivirus o de tiempo de arranque.
#
# exe = EXE(
#     pyz,
#     a.scripts,
#     [],
#     exclude_binaries=True,
#     name=NOMBRE,
#     console=True,
#     upx=True,
# )
# coll = COLLECT(exe, a.binaries, a.datas, name=NOMBRE)
