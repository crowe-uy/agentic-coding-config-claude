---
name: commit-pr
description: Revisa el cambio, arma el commit con el formato del equipo y abre el pull request con el detalle de funcionalidad y pruebas, y registra la entrada en la bitácora. Usalo al cerrar cada tarea de desarrollo.
---

# Commit y pull request

Cierra una tarea de la Fase 2. El PR es lo que otra persona va a leer para decidir si el cambio entra: tiene que explicarse solo.

## 1. Revisá antes de commitear

Pasá el agente `revisor-codigo` sobre el cambio. Si informa algo **bloqueante** (secretos, pruebas que fallan, cambio sin pruebas, error mal clasificado), corregilo antes de seguir.

Después, verificá con tus propios ojos:

```bash
git status
git diff
python -m pytest
ruff check .
```

## 2. Confirmá la rama

```bash
git branch --show-current
```

Tiene que ser `feature/*` o `fix/*`. Si estás en `dev` o `main`, creá la rama correcta y llevate los cambios; el control de git va a bloquear el commit de todos modos.

## 3. Armá el commit

Formato: `tipo: descripción concisa en presente`.

Tipos: `funcionalidad`, `correccion`, `pruebas`, `documentacion`, `refactor`, `mantenimiento`.

El cuerpo responde **qué cambia, por qué y qué se probó**:

```
funcionalidad: descarga el resumen mensual del portal del proveedor

Agrega el conector web con reintentos ante timeout y validación del
PDF descargado. Cubre CU-003 y CU-004.

Pruebas: CP-007, CP-008 (unitarias, OK) y CP-012 (integración, OK).
```

Un commit cuyo cuerpo no menciona pruebas está incompleto. Agregá solo los archivos del cambio: nada de `git add .` a ciegas.

## 4. Abrí el pull request

```bash
git push -u origin <rama>
gh pr create --base dev --title "<mismo formato que el commit>" --body-file <archivo>
```

El cuerpo completa la plantilla del proyecto: qué cambia (en lenguaje entendible), por qué, casos de uso cubiertos, tabla de pruebas ejecutadas con su resultado, documentación actualizada, verificaciones y riesgos.

**Siempre a `dev`.** Solo `release/*` y `hotfix/*` van a `main`.

## 5. Registrá en la bitácora

Agregá la entrada a `docs/bitacora.md`: fecha, fase, responsable, qué se hizo, decisiones tomadas con sus alternativas descartadas, número y título del PR, casos de prueba ejecutados y pendientes.

Si durante la tarea asumiste algo sin confirmar, **registralo como supuesto**: es lo que evita que dentro de tres meses nadie sepa por qué el bot hace lo que hace.

## 6. Contale al desarrollador

Resumí: qué quedó en el PR, qué falta para completar el alcance del diseño, y qué conviene mirar con atención en la revisión.
