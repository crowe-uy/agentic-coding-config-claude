---
name: bitacora
description: Agrega una entrada a la bitácora del ciclo de implementación registrando una decisión, una aprobación, un pull request, una prueba o un incidente. Usalo en cada hito del ciclo.
---

# Entrada en la bitácora

`docs/bitacora.md` es el registro histórico del ciclo. Es lo que permite, dentro de un año, entender por qué la automatización es como es.

## Regla

**Se agregan entradas al final. Nunca se editan ni se borran las anteriores.** Si algo se decidió mal, se escribe una entrada nueva que lo corrige y explica por qué cambió el criterio.

## Formato

```
## [AAAA-MM-DD] Fase N — Título
**Responsable:** Nombre
**Qué pasó:** ...
**Decisiones:** ... (con las alternativas descartadas y por qué)
**PR:** #NN rama-origen → rama-destino — detalle
**Pruebas:** CP-00X (tipo, resultado)
**Pendientes / riesgos:** ...
```

Usá la fecha real de hoy, no un marcador.

## Qué registrar

Siempre generan entrada:

- el alta del proyecto;
- el cierre del relevamiento, con el hash del documento;
- la aprobación del diseño: quién aprobó, cuándo y con qué observaciones;
- cada PR mergeado;
- cada release, incluyendo si el diagrama se actualizó o quedó sin cambios;
- cada incidente en producción y cómo se resolvió;
- **cada supuesto que se asumió sin confirmación del referente.**

## Lo que importa

El **por qué**, no el qué. Lo que se hizo ya está en el código y en el historial de git; lo que se pierde es el razonamiento: qué alternativa se evaluó, por qué se descartó, qué restricción del negocio obligó a esa solución.

Una entrada útil dice "se descartó procesar en paralelo porque el portal bloquea la sesión ante accesos simultáneos". Una entrada inútil dice "se implementó el conector".

## Antes de escribir

Si el desarrollador no dio todos los datos, preguntá lo que falte: responsable, decisión tomada, número de PR, casos de prueba ejecutados. Una entrada a medias no sirve como registro.
