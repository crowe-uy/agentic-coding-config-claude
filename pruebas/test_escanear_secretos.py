"""Pruebas del escáner de secretos.

Es el control que impide que una credencial llegue al repositorio: sus falsos
negativos son incidentes de seguridad y sus falsos positivos frenan al equipo.
"""

from __future__ import annotations

import escanear_secretos


def _motivos(texto: str, nombre: str = "src/ejemplo.py") -> list[str]:
    return [h.motivo for h in escanear_secretos.escanear_texto(nombre, texto)]


def test_detecta_una_credencial_asignada() -> None:
    """Una clave literal en el código se detecta."""
    assert _motivos('CLAVE_PORTAL = "Sup3rS3cr3t0_2026"')


def test_detecta_token_de_github() -> None:
    """Un token con prefijo conocido se detecta por patrón."""
    falso = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    assert _motivos(f'token = "{falso}"')


def test_detecta_cadena_de_alta_entropia() -> None:
    """Una cadena larga y aleatoria se marca aunque no tenga prefijo conocido."""
    assert _motivos('valor = "aGVsbG8gd29ybGQgZXN0byBlcyB1bmEgY2FkZW5hIG11eSBsYXJnYQ=="')


def test_no_marca_una_lectura_de_variable_de_entorno() -> None:
    """La forma correcta de leer una credencial no es un hallazgo."""
    assert not _motivos('clave = obtener_variable("PORTAL_CLAVE")')


def test_no_marca_una_interpolacion() -> None:
    """Un encabezado armado con una variable no es un secreto literal."""
    assert not _motivos('encabezados = {"Authorization": f"Bearer {self._token}"}')


def test_no_marca_un_valor_de_ejemplo() -> None:
    """Los marcadores de plantilla no son secretos."""
    assert not _motivos('PASSWORD = "placeholder"')


def test_respeta_la_exencion_explicita() -> None:
    """El comentario de exención permite convivir con un falso positivo."""
    assert not _motivos('clave = "hunter2000"  # escaneo-ok: dato ficticio de prueba')


def test_bloquea_el_documento_de_relevamiento() -> None:
    """El relevamiento no puede versionarse."""
    hallazgo = escanear_secretos.revisar_ruta("relevamiento/Relevamiento Cliente.docx")
    assert hallazgo is not None
    assert "relevamiento" in hallazgo.motivo


def test_bloquea_el_archivo_env() -> None:
    """El .env con credenciales no puede versionarse."""
    assert escanear_secretos.revisar_ruta(".env") is not None


def test_permite_el_env_de_ejemplo() -> None:
    """El .env.example sí se versiona: documenta las variables sin sus valores."""
    assert escanear_secretos.revisar_ruta(".env.example") is None
    assert not _motivos("PORTAL_CLAVE=", nombre=".env.example")


def test_detecta_secretos_en_las_lineas_agregadas_de_un_diff() -> None:
    """El modo diff solo mira lo que se agrega."""
    diff = '+++ b/src/config.py\n@@ -1,0 +1,2 @@\n+CLAVE_SAP = "Produccion_2026"\n-borrado = 1\n'
    assert escanear_secretos.escanear_diff(diff, ["src/config.py"])
