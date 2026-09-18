---
name: empaquetar
description: Genera un .exe standalone del bot con PyInstaller, para equipos del cliente donde no se puede instalar Python. Paso opcional de la Fase 4/5, después de un release aprobado.
---

# Empaquetado en .exe

Opcional: solo si el equipo donde va a correr el bot no puede tener Python instalado. Si puede, `python ejecutar.py` alcanza y no hace falta nada de esto.

Se empaqueta **sobre un release ya aprobado**, nunca sobre trabajo sin terminar: el `.exe` tiene que corresponder exactamente a un commit tagueado.

## 1. Pará sobre el commit correcto

```bash
git status        # debe estar todo commiteado
git checkout vX.Y.Z
```

Si estás construyendo el `.exe` como parte de cerrar el release, alcanza con estar en `main` recién mergeado.

## 2. Instalá las dependencias, incluido PyInstaller

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

`pyinstaller` ya está en `requirements-dev.txt` de la plantilla.

## 3. Compilá

```bash
pyinstaller paquete.spec
```

Genera `dist/<paquete>.exe`. El `.spec` viene con el nombre del paquete ya reemplazado desde `/nuevo-bot`.

## 4. Renombrá con la versión

```bash
ren dist\<paquete>.exe <paquete>-X.Y.Z.exe
```

Así el archivo entregado queda trazable a un release concreto.

## 5. Probalo desde otra carpeta

No lo pruebes desde `dist/` en la misma sesión de compilación: copialo (o corré desde otra carpeta) para confirmar que realmente no depende del directorio desde donde se lo compiló.

```bash
mkdir C:\prueba-exe
copy dist\<paquete>-X.Y.Z.exe C:\prueba-exe\
copy .env.example C:\prueba-exe\.env.local
REM completar C:\prueba-exe\.env.local con valores de prueba
cd C:\prueba-exe
<paquete>-X.Y.Z.exe
```

Verificá:

- `logs/` y `salida/` aparecen en `C:\prueba-exe\`, no en la carpeta del proyecto.
- El código de salida es el esperado (0 procesado, 2 si falta configuración).
- Si el bot usa `ConectorWeb` (Playwright), confirmá que el equipo destino tiene el navegador instalado — el `.exe` no lo incluye. Ver `docs/empaquetado.md` del plugin.

## 6. Entregalo

Dos formas razonables — elegí según cómo distribuya el equipo:

```bash
gh release create vX.Y.Z dist/<paquete>-X.Y.Z.exe --title "vX.Y.Z" --notes "Ver docs/pruebas/releases/X.Y.Z/index.html"
```

o copiarlo directo al equipo del cliente junto con `.env`, `recursos/` y, si la parametrización real es local y no una carpeta de red, esos archivos también.

## 7. Documentá en el manual de usuario

Agregá en `docs/manual-usuario.md`, sección "Cómo ejecutar la automatización": que corre como `.exe` (no requiere Python instalado), dónde tiene que vivir el `.env`/`.env.local`/`.env.dev` (junto al `.exe`, siempre), y cómo reconstruirlo si hace falta un cambio.

## Al terminar

Registrá en la bitácora: versión empaquetada, cómo se entregó (release de GitHub / copia directa) y a quién.
