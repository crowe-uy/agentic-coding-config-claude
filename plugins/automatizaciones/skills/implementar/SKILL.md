---
name: implementar
description: Organiza el desarrollo a partir del diseño aprobado: descompone en tareas, propone las ramas feature o fix, y escribe el código junto con sus pruebas siguiendo los estándares del equipo. Fase 2 del ciclo.
---

# Desarrollo

Fase 2 del ciclo. El diseño ya está aprobado; ahora se construye.

## 1. Confirmá que el diseño está aprobado

Leé `docs/diseno/solucion.md` y buscá la fila **Aprobado por**. Si está vacía o tiene un marcador `<...>`, **frená**: no se escribe código productivo sin diseño aprobado. Decilo claramente y ofrecé `/diseno`.

## 2. Descomponé el trabajo

A partir del diagrama y de la matriz de casos de uso, armá la lista de tareas. Un buen corte:

1. Estructura y configuración: `configuracion.py`, `.env.example`, validación al arrancar.
2. Un conector por sistema externo, uno por vez, con sus pruebas de integración contra dobles.
3. Las reglas de negocio, con sus pruebas unitarias.
4. El orquestador `principal.py`, siguiendo el diagrama.
5. El informe de resultado y las notificaciones.

Cada tarea es una rama `feature/<slug>` (o `fix/<slug>` si corrige algo ya integrado en `dev`), nace de `dev` y vuelve a `dev` por PR. Proponé la lista y confirmala con el desarrollador antes de arrancar.

Preferí varias ramas chicas a una grande: un PR que toca cuatro cosas es un PR que nadie revisa bien.

## 3. Creá la rama

```bash
git checkout dev
git pull
git checkout -b feature/<slug>
```

El slug va en minúsculas, con guiones, sin tildes: `feature/conector-portal-afip`.

## 4. Implementá

Usá el agente `implementador`, que tiene los estándares del equipo. Las reglas que más importan:

- El flujo de `principal.py` se lee como el diagrama.
- Todo sistema externo va detrás de un conector usado con `with`.
- Cada error se clasifica: `ErrorNegocio` (no se reintenta) o `ErrorSistema` (se reintenta).
- Esperas por condición, nunca `time.sleep()` fijo.
- Las credenciales se leen con `obtener_variable(...)` y la variable se agrega a `.env.example` en el mismo cambio.
- **Código y pruebas se escriben juntos.** Cada cambio de comportamiento lleva su prueba y su caso en `docs/pruebas/casos.toml`.

Mientras trabajás, el control de calidad formatea y revisa cada archivo Python que se edita, y te devuelve lo que queda por corregir. Corregilo en el momento.

## 5. Verificá antes de cerrar la tarea

```bash
python -m pytest
ruff check .
```

Las dos cosas en verde. Si una prueba existente falla por tu cambio, actualizala; no la borres ni la marques como omitida.

## 6. Cerrá con el PR

Pasá el agente `revisor-codigo` y después usá `/commit-pr`.

## Si el diseño no alcanza

Si al implementar descubrís que el diseño está mal o incompleto, **no lo resuelvas en silencio**. Avisá al desarrollador, actualizá `docs/diseno/solucion.md` y registrá el cambio en la bitácora. El diagrama y el código tienen que seguir contando la misma historia.
