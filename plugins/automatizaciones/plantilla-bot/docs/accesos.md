# Verificación de accesos — <NOMBRE_DEL_BOT>

Comprobación de que el desarrollador y el bot pueden entrar realmente a todo lo que la solución necesita. **Se cierra antes de diseñar**: descubrir en la semana tres que falta un permiso es la causa más común de atraso en una automatización.

> **Nunca se escriben credenciales en este archivo.** Acá se registra *qué* acceso hace falta y *si ya funciona*, no con qué usuario ni con qué clave.

## Estado general

| # | Sistema / recurso | Tipo de acceso | Solicitado a | Fecha solicitud | Fecha verificación | Estado |
|---|---|---|---|---|---|---|
| A-001 | | usuario de aplicación / permiso / carpeta de red / casilla / equipo | | AAAA-MM-DD | AAAA-MM-DD | pendiente |

Estados: `pendiente` (todavía no se pidió) · `solicitado` (pedido, sin respuesta) · `verificado` (se probó y funciona).

**Verificado significa que se entró y se hizo la operación**, no que alguien avisó que el acceso estaba dado.

## Ambiente de pruebas

| Sistema | ¿Hay ambiente de prueba? | Datos de prueba disponibles | Observaciones |
|---|---|---|---|
| | sí / no | sí / no | |

Si un sistema no tiene ambiente de prueba, se registra acá cómo se van a probar los casos que lo involucran: esos casos probablemente sean manuales en el informe del release.

## Equipo de ejecución

| | |
|---|---|
| **Dónde corre el bot** | equipo del desarrollador / servidor / VM |
| **Sistema operativo y versión** | |
| **Versión de Python** | |
| **Software adicional requerido** | (SAP GUI, Office, driver de impresora, etc.) |
| **Quién administra el equipo** | |
