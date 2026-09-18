---
name: relevamiento
description: Lee el documento de relevamiento (Word o PDF) de la carpeta local, lo interpreta y genera el resumen sanitizado y las preguntas abiertas para el referente. Primer paso de la Fase 1.
---

# Lectura e interpretación del relevamiento

Fase 1 del ciclo. Convierte el documento del cliente en información versionable y detecta lo que falta definir.

## 1. Ubicá el documento

Buscá en `relevamiento/` un archivo `.docx` o `.pdf`. Si hay varios, preguntá cuál es el vigente. Si no hay ninguno, pedile al desarrollador que lo deje ahí y explicale que esa carpeta está ignorada por git a propósito.

## 2. Extraé el texto

Para `.docx`:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/leer_documento.py" "relevamiento/<archivo>.docx"
```

Para `.pdf`: leelo con la herramienta Read.

Guardá el SHA-256 que informa el script (o generalo con `--solo-hash`): va en el resumen para dejar constancia de qué versión exacta del documento se relevó.

## 3. Interpretá y documentá

Usá el agente `analista-relevamiento` para producir los tres artefactos. Tiene las instrucciones completas de qué extraer, qué preguntar y qué sanitizar.

Resultado esperado:

- `docs/relevamiento-resumen.md` — objetivo, alcance, sistemas, entradas y salidas, reglas de negocio `RN-00X`, excepciones `EX-00X`, parametrizaciones, volumen y criterio de éxito. **Sanitizado**: sin nombres de personas, CUIT, montos, credenciales ni rutas internas.
- `docs/preguntas-abiertas.md` — todo lo que el documento no aclara, incluidos los sistemas a los que el desarrollador todavía no puede entrar.

Los accesos no llevan un documento aparte: el desarrollador los prueba directamente (con `.env.local` o `.env.dev`, nunca versionados) antes de diseñar. Si alguno no funciona, es una pregunta abierta, no un dato a completar más adelante.

## 4. Repasá con el desarrollador

Presentale:

- qué entendiste que hace la automatización, en tres oraciones;
- **las preguntas bloqueantes**, separadas de las menores;
- qué accesos convendría empezar a gestionar ya, porque suelen tardar;
- los riesgos que ves en el alcance.

Las preguntas se resuelven con el referente **antes** de diseñar. Una pregunta abierta al momento de diseñar es un rediseño garantizado.

## 5. Registrá

Agregá la entrada correspondiente en `docs/bitacora.md`: fecha, documento relevado con su hash y qué quedó pendiente de definir.

## Al terminar

Si no quedan preguntas abiertas, el siguiente paso es `/diseno`. Si quedan preguntas, decilo explícitamente: el ciclo no avanza hasta resolverlas.
