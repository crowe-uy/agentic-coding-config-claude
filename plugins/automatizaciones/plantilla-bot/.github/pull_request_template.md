## Qué cambia

<Explicalo de forma que lo entienda alguien que no leyó el código.>

## Por qué

<El caso de uso, el hallazgo de una prueba o el incidente que lo origina.>

## Casos de uso cubiertos

<CU-00X del diseño. Si el PR no cubre ninguno, explicá por qué.>

## Pruebas ejecutadas

| Caso | Tipo | Resultado |
|---|---|---|
| CP-00X | automatizada / manual | OK / falla |

```
<Salida resumida de python -m pytest>
```

## Documentación actualizada

- [ ] Bitácora (`docs/bitacora.md`)
- [ ] Diagrama de la solución, si el diseño cambió
- [ ] Manual de usuario, si cambió una precondición, una parametrización o un error contemplado
- [ ] `.env.example`, si se agregó una variable de entorno
- [ ] Catálogo de pruebas (`docs/pruebas/casos.toml`)

## Verificaciones

- [ ] `python -m pytest` pasa completo
- [ ] `ruff check .` sin hallazgos
- [ ] No hay credenciales, datos reales ni el documento de relevamiento en el diff
- [ ] La rama destino es la correcta (`feature/*` y `fix/*` van a `dev`; solo `release/*` y `hotfix/*` van a `main`)

## Riesgos y qué mirar en la revisión

<Qué puede romperse, qué quedó fuera de alcance, dónde conviene que el revisor mire con atención.>
