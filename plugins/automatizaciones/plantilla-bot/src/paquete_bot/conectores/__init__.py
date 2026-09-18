"""Conectores: un módulo por sistema externo.

`principal.py` nunca llama directo a Playwright, pywinauto o httpx. Todo pasa
por un conector, y eso permite tres cosas: leer el flujo sin ruido técnico,
probarlo con un doble sin abrir un navegador, y cambiar de tecnología tocando
un solo archivo.
"""
