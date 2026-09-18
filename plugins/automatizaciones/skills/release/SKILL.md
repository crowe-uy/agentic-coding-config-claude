---
name: release
description: Prepara el release de la automatización, crea la rama release/X.Y.Z, ejecuta la batería completa de pruebas, genera el informe index.html con la evidencia y verifica que el ciclo esté completo antes del pase a producción. Fase 4 del ciclo.
---

# Release y evidencia de pruebas

Fase 4 del ciclo. Termina con la validación del desarrollador y del referente **antes** del merge a `main`.

## 1. Elegí la versión

Versionado semántico `X.Y.Z`:

- **mayor**: cambia el alcance funcional o rompe la parametrización existente;
- **menor**: funcionalidad nueva compatible;
- **parche**: correcciones sin cambios funcionales.

Mirá los tags existentes (`git tag`) y proponé la versión siguiente. Confirmala con el desarrollador.

## 2. Verificá que el manual esté al día

El manual de usuario debe estar escrito y en la versión de este release. Si no lo está, ejecutá `/manual-usuario` antes de seguir.

## 3. Creá la rama de release

```bash
git checkout dev
git pull
git checkout -b release/X.Y.Z
git push -u origin release/X.Y.Z
gh pr create --base release/X.Y.Z --head dev --title "release: X.Y.Z" --body "<alcance del release>"
```

A partir de acá, en `release/X.Y.Z` solo entran correcciones de lo que encuentren las pruebas. Funcionalidad nueva va a `dev` y sale en el próximo release.

## 4. Completá el catálogo de casos

Usá el agente `ingeniero-pruebas`. Tiene que verificar que **cada `CU-00X` de la matriz del diseño tenga al menos un caso** en `docs/pruebas/casos.toml`. Si falta alguno, se escribe la prueba o se agrega como caso manual con pasos concretos.

## 5. Ejecutá todo

```bash
python -m pytest -m "" --junitxml=resultados-pytest.xml
```

El `-m ""` incluye las pruebas `e2e`, que quedan fuera de la corrida diaria pero sí corren en el release.

**Si algo falla, el release se detiene.** Se corrige en `fix/<slug>` sobre `release/X.Y.Z`, se vuelve a correr y recién ahí se sigue. No se omite ni se ajusta una prueba para que pase.

## 6. Cargá las pruebas manuales

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/generar_informe.py" --version X.Y.Z --responsable "<desarrollador>" --referente "<referente>"
```

La primera corrida crea `docs/pruebas/releases/X.Y.Z/resultados-manuales.toml` con un bloque por caso manual. El desarrollador las ejecuta y vos completás estado, resultado obtenido, responsable y evidencia.

Las capturas van en `docs/pruebas/releases/X.Y.Z/evidencias/`, **anonimizadas**: sin CUIT, nombres de clientes ni montos reales.

Volvé a generar el informe con los resultados cargados.

## 7. Corré la validación

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/verificar_ciclo.py" --fase release --version X.Y.Z
```

Controla cobertura de casos de uso, casos fallidos o sin ejecutar, secciones del manual, versión del manual, entrada de bitácora, revisión del diagrama, variables documentadas y archivos sensibles versionados.

**Si algo falla, no se abre el PR a `main`.** Resolvé y volvé a correr.

## 8. Abrí el pull request a producción

```bash
git add docs/
git commit -m "documentacion: informe de pruebas y manual del release X.Y.Z"
git push
gh pr create --base main --head release/X.Y.Z --title "release: X.Y.Z" --body-file <archivo>
```

El cuerpo incluye: alcance del release, resultado de las pruebas (totales y porcentaje), ruta del informe, cambios en el manual, si el diagrama se actualizó, y qué tienen que validar el desarrollador y el referente.

**La validación ocurre antes del merge.** Un PR abierto no es un pase a producción.

## 9. Después del merge

```bash
git checkout main && git pull
git tag -a vX.Y.Z -m "Release X.Y.Z"
git push origin vX.Y.Z
git checkout dev && git merge main && git push
```

El **back-merge a `dev`** no es opcional: sin él, las correcciones del release se pierden y el próximo release reintroduce bugs ya resueltos.

Cerrá con la entrada en `docs/bitacora.md`: versión, resultado de las pruebas, quién validó y qué quedó pendiente para la próxima versión.
