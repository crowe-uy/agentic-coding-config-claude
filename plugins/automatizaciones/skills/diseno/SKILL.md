---
name: diseno
description: Diseña la solución de la automatización y la documenta como diagrama de flujo en Mermaid con su matriz de casos de uso, y prepara el pull request para que el referente técnico la apruebe. Segundo paso de la Fase 1.
---

# Diseño de la solución y aprobación del referente

Fase 1 del ciclo. Termina con la aprobación del referente técnico. **No se escribe código productivo antes de esa aprobación.**

## 1. Verificá que se pueda diseñar

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/verificar_ciclo.py" --fase diseno
```

Va a marcar como faltante la aprobación (todavía no existe) y eso está bien. Lo que sí tiene que estar en orden:

- `docs/relevamiento-resumen.md` completo;
- **cero preguntas en estado `abierta`**.

Si quedan preguntas abiertas, frená y decí cuáles. Diseñar sobre supuestos sin confirmar es la forma más cara de equivocarse. Verificá también, de palabra con el desarrollador, que ya probó el acceso a cada sistema del relevamiento — si no, es una pregunta abierta más.

## 2. Diseñá

Usá el agente `disenador-solucion`, que tiene las convenciones del diagrama y el criterio para armar la matriz de casos de uso.

Resultado: `docs/diseno/solucion.md` con el diagrama Mermaid, los módulos, el manejo de errores, la idempotencia y reanudación, las parametrizaciones, las decisiones de diseño y la matriz `CU-00X`.

## 3. Revisalo con el desarrollador antes del PR

Mostrale el diagrama y repasá en voz alta:

- ¿El flujo es el que esperaba?
- ¿Están dibujados los caminos de error, no solo el feliz?
- ¿Cada excepción del relevamiento aparece en el diagrama y en la tabla de manejo de errores?
- ¿La matriz de casos de uso cubre los bordes: cero ítems, volumen máximo, reejecución?

Corregí antes de abrir el PR: es más barato que corregir después de la revisión del referente.

## 4. Abrí el pull request para la aprobación

```bash
git checkout -b feature/diseno-inicial
git add docs/
git commit -m "documentacion: diseño de la solución para aprobación del referente"
git push -u origin feature/diseno-inicial
gh pr create --base dev --title "documentacion: diseño de la solución" --body-file <cuerpo>
```

El cuerpo del PR usa la plantilla del proyecto y tiene que decir: qué automatiza, cuántos sistemas toca, qué decisiones de diseño necesitan confirmación, y qué preguntas se resolvieron con quién.

Pedile explícitamente al referente lo que tiene que validar: el flujo, el manejo de excepciones y la matriz de casos de uso.

## 5. Cuando lo aprueben

Completá en `docs/diseno/solucion.md` la fila **Aprobado por** y la fecha, agregá la entrada a `docs/bitacora.md` con quién aprobó y qué observaciones dejó, y volvé a correr:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/verificar_ciclo.py" --fase diseno
```

Con la aprobación registrada, el siguiente paso es `/implementar`.
