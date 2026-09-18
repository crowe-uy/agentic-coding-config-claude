---
name: nuevo-bot
description: Crea una automatización nueva desde la plantilla del equipo, con la estructura de código, las plantillas del ciclo, git inicializado en main y dev, y los controles de seguridad instalados. Usalo al arrancar cualquier automatización.
---

# Alta de una automatización nueva

Fase 0 del ciclo. Deja el proyecto listo para recibir el relevamiento.

## 1. Averiguá lo mínimo

Preguntá al desarrollador, si no lo dijo al invocar el comando:

- **Nombre del bot**, legible: "Facturación de proveedores".
- **Dónde crearlo**: carpeta destino. Si no la dice, proponé una carpeta hermana de la actual con el nombre en minúsculas y guiones.
- **Referente técnico**: su usuario de GitHub (o `org/equipo`). Es quien va a aprobar el diseño y validar cada release; va directo a `CODEOWNERS`. Si todavía no lo sabe, seguí sin este dato — pero avisale que hay que completarlo antes de activar la protección de ramas.

Derivá el nombre del paquete de Python: minúsculas, sin tildes ni `ñ`, con guiones bajos, corto. De "Facturación de proveedores" → `facturacion_proveedores` (sacá las preposiciones).

## 2. Creá el proyecto

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/preparar_proyecto.py" --destino "<ruta>" --nombre "<nombre legible>" --paquete <paquete> --referente <usuario-o-org/equipo>
```

Omití `--referente` si todavía no lo tenés; el script va a avisar que `CODEOWNERS` quedó pendiente.

El script copia la plantilla, la personaliza, inicializa git en `main`, hace el commit inicial, crea `dev` y deja instalados el escáner de secretos y el control previo al commit.

Si informa que git no tiene identidad configurada, decile al desarrollador que ejecute `git config --global user.name` y `user.email`, y hacé el commit inicial después.

## 3. Verificá que quedó bien

Desde la carpeta nueva:

```bash
git branch -a
python -m pytest
```

Deben existir `main` y `dev`, estar parado en `dev`, y las pruebas de ejemplo deben pasar. Si `pytest` no está instalado todavía, es esperable: se instala en el paso siguiente.

## 4. Decile al desarrollador cómo seguir

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
copy .env.example .env.local
```

Y los tres pasos inmediatos del ciclo:

1. Guardar el documento de relevamiento en `relevamiento/` (esa carpeta no se sube nunca).
2. Ejecutar `/relevamiento`.
3. Crear el repositorio remoto cuando esté listo: `gh repo create <nombre> --private --source=. --push`, y configurar en GitHub la protección de `main` y `dev` según `docs/convenciones-git.md` del plugin.

## 5. Abrí la bitácora

Completá la primera entrada de `docs/bitacora.md` con la fecha real, el nombre del desarrollador y el estado inicial. Reemplazá los marcadores `<...>` del `README.md` del proyecto con lo que sepas.

## Antes de terminar

Recordale al desarrollador las dos reglas que más se olvidan al empezar:

- El relevamiento **no se sube**, ni siquiera "por un rato".
- No se escribe código productivo hasta que el referente apruebe el diseño.
