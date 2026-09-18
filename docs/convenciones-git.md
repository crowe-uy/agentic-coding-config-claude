# Convenciones de Git y GitHub

## Ramas

| Rama | Rol | Nace de | Vuelve a |
|---|---|---|---|
| `main` | **Productiva.** Refleja exactamente lo que corre en producción | — | — |
| `dev` | Integración de cambios durante desarrollo y pruebas | `main` | — |
| `feature/<slug>` | Funcionalidad nueva | `dev` | `dev` |
| `fix/<slug>` | Ajuste o corrección durante el desarrollo | `dev` | `dev` |
| `release/X.Y.Z` | Estabilización y evidencia de pruebas antes de producción | `dev` | `main` y `dev` |
| `hotfix/<slug>` | Corrección urgente de un incidente en producción | `main` | `main` y `dev` |

Reglas que el plugin hace cumplir automáticamente:

- **Nunca se commitea ni se pushea directo a `main` ni a `dev`.** Todo entra por PR.
- **Nunca `push --force`** sobre ramas compartidas.
- `feature/*` y `fix/*` **no** pueden mergear a `main`: solo `release/*` y `hotfix/*` llegan a producción.
- Después de cada merge a `main` hay **back-merge a `dev`**. Sin excepción: sin eso, el próximo release reintroduce bugs ya corregidos.

El slug va en minúsculas, con guiones y sin tildes: `feature/descarga-facturas-afip`, `fix/reintento-timeout-sap`.

## Versionado

Versionado semántico `X.Y.Z`:

- **X (mayor):** cambia el alcance funcional del bot o rompe la parametrización existente.
- **Y (menor):** funcionalidad nueva compatible con la parametrización actual.
- **Z (parche):** corrección de errores, sin cambios funcionales.

La rama se llama `release/1.2.0`; el tag en `main`, `v1.2.0`. La misma versión identifica al bot, al informe de pruebas y a la entrada del manual de usuario.

## Mensajes de commit

Formato: `tipo: descripción concisa en presente`.

| Tipo | Cuándo |
|---|---|
| `funcionalidad` | Comportamiento nuevo del bot |
| `correccion` | Arreglo de un error |
| `pruebas` | Casos de prueba nuevos o actualizados |
| `documentacion` | Bitácora, manual, diseño, README |
| `refactor` | Cambio interno sin alterar el comportamiento |
| `mantenimiento` | Dependencias, configuración, tareas de soporte |

```
funcionalidad: descarga el resumen mensual del portal del proveedor

Agrega el conector web con reintentos ante timeout y validación del
PDF descargado. Cubre CU-003 y CU-004.

Pruebas: CP-007, CP-008 (unitarias, OK) y CP-012 (integración, OK).
```

El cuerpo responde tres preguntas: **qué cambia, por qué y qué se probó**. Un commit cuyo cuerpo no menciona pruebas es un commit incompleto.

> Equivalencia con Conventional Commits, por si más adelante se automatiza el changelog: `funcionalidad`→`feat`, `correccion`→`fix`, `pruebas`→`test`, `documentacion`→`docs`, `refactor`→`refactor`, `mantenimiento`→`chore`.

## Pull requests

Cada PR usa la plantilla del proyecto (`.github/pull_request_template.md`) y responde:

1. **Qué cambia** — en lenguaje entendible por alguien que no leyó el código.
2. **Por qué** — el caso de uso o el incidente que lo origina.
3. **Casos de uso cubiertos** — `CU-00X` del diseño.
4. **Pruebas ejecutadas** — ids del catálogo, tipo y resultado.
5. **Riesgos y qué mirar en la revisión.**

Títulos con el mismo formato que los commits. Un PR por funcionalidad: si el título necesita un "y", probablemente sean dos PR.

## Protección de ramas en GitHub

Configuración recomendada, a aplicar por quien administre el repositorio:

- `main`: PR obligatorio, 1 aprobación de CODEOWNERS, sin push directo, sin force-push, historial lineal.
- `dev`: PR obligatorio, sin push directo.
- `CODEOWNERS` asigna `docs/diseno/` y `docs/manual-usuario.md` al referente técnico, para que las dos aprobaciones del ciclo pasen por él.

## Qué nunca entra al repositorio

El documento de relevamiento, archivos `.env`, credenciales, certificados, datos reales de clientes y capturas con información sensible. El detalle y los controles automáticos están en [seguridad.md](seguridad.md).
