---
name: manual-usuario
description: Genera o actualiza el manual de usuario para el equipo de mantenimiento, con precondiciones, postcondiciones, parametrizaciones, errores contemplados y conocidos, y su tabla de versiones. Fase 3, antes del release.
---

# Manual de usuario

Fase 3 del ciclo. Se escribe **antes** del release, porque es uno de los documentos que exige la validación previa a producción.

El lector es el equipo de mantenimiento: no desarrolló el bot y va a leer esto cuando algo falle.

## 1. Juntá la información

Leé, en este orden:

- `docs/diseno/solucion.md` — el flujo y el manejo de errores;
- `src/` — las variables de entorno que se usan realmente, los mensajes de error tal como aparecen en el log, los códigos de salida;
- `docs/relevamiento-resumen.md` — las parametrizaciones y el criterio de éxito del negocio;
- `docs/bitacora.md` — los problemas que aparecieron durante el desarrollo: varios son "errores conocidos".

## 2. Escribí o actualizá

Usá el agente `documentador`. Las seis secciones son obligatorias y el verificador del release las controla por nombre:

`## Precondiciones` · `## Postcondiciones y resultados` · `## Parametrizaciones` · `## Errores contemplados` · `## Errores conocidos` · `## Versiones del manual`

Criterios que marcan la diferencia entre un manual que se usa y uno que se ignora:

- **Cada precondición dice cómo verificarla.** Una que no se puede verificar no sirve.
- **Los mensajes de error van textuales**, como aparecen en el log: el soporte busca por ahí.
- **Los errores conocidos incluyen cómo replicarlos** paso a paso, y quién es responsable de resolverlos: el equipo, el cliente o el proveedor del sistema.
- **La tabla de parametrizaciones va columna por columna**, con tipo, obligatoriedad, validación y ejemplo, y las reglas al modificar el archivo.
- Lenguaje llano: "reintenta tres veces y después marca el ítem", no el nombre del decorador.

## 3. Revisá el diagrama

Comparado con lo que el bot hace hoy, ¿`docs/diseno/solucion.md` sigue siendo correcto?

- **Si cambió**, actualizá el diagrama y agregá una fila al historial del diseño.
- **Si no cambió**, declaralo explícitamente en la bitácora: el verificador del release lo exige y no acepta silencio.

## 4. Versioná el manual

Agregá la fila a `## Versiones del manual`: versión del manual, versión del bot del release, fecha, cambios y autor. Actualizá también el encabezado del documento.

## 5. Registrá

Entrada en `docs/bitacora.md`: manual actualizado a la versión X, y si el diagrama se actualizó o quedó sin cambios.

## Al terminar

Contale al desarrollador qué secciones quedaron incompletas por falta de información (típicamente: quién provee cada credencial, el horario de ejecución programada y los contactos) para que las complete antes del release.
