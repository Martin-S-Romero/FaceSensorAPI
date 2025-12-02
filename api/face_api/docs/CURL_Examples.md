# Uso de la API con curl

Este documento muestra ejemplos detallados de llamadas a la API usando `curl` (bash) para los endpoints principales de la API FaceCensor.
Incluye:
- Autenticación (obtención de token OAuth2)
- Procesamiento de imagen — envío por path (archivo) y por URL
- Procesamiento de video — envío por path (archivo) y por URL

Notas generales:
- La aplicación FastAPI en tu proyecto monta la versión 1 bajo el prefijo `/v1`. Por tanto los endpoints son:
  - `POST /v1/process/image`
  - `POST /v1/process/video`
- El endpoint de autenticación es `POST /auth/login` y devuelve JSON con `access_token`.
- Para usar las rutas protegidas incluye el header: `Authorization: Bearer <TOKEN>`.
- Los campos de formulario esperados (en `v1`) son:
  - `user` (string) — requerido
  - `id` (string) — requerido
  - `file` (multipart file) — opcional si envías `url`
  - `url` (string) — opcional si envías `file`
  - `mode` (string) — opcional, por defecto `blur` (ej. `blur`, `pixelate`)
  - `expand` (int) — opcional, por defecto `10`
  - `blur_strength` (int) — opcional, por defecto `55`
  - `pixel_size` (int) — opcional, por defecto `10`
  - `cut` (bool) — opcional, por defecto `false`

Ejemplos asumidos en las llamadas:
- Host: `http://127.0.0.1:8000` (ajusta si tu servidor usa otro host/puerto)
- Usuario de ejemplo: `martin` / contraseña `123456` (el proyecto tiene un usuario falso con estas credenciales)
- http://127.0.0.1:8000/docs
---

## 1) Autenticación (obtener token)

Descripción: llama a `POST /auth/login` usando `application/x-www-form-urlencoded` con los campos `username` y `password` (OAuth2PasswordRequestForm).

Ejemplo curl (bash):

```bash
curl -i -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Accept: application/json" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=martin&password=123456"
```

Explicación de opciones:
- `-i` incluida la cabecera HTTP en la salida (útil para depuración).
- `-X POST` fuerza el método POST.
- `-H` añade headers: aceptamos JSON y declaramos el tipo de contenido del body.
- `-d` envía los campos `username` y `password` en formato urlencoded.

Respuesta esperada (JSON):

```json
{
  "access_token": "<JWT_TOKEN_AQUI>",
  "token_type": "bearer"
}
```

Cómo extraer el token en bash (ej.: usando `jq`):

```bash
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=martin&password=123456" | jq -r '.access_token')
echo "Token: $TOKEN"
```

Nota para PowerShell (Windows): el alias `curl` en PowerShell v5.1 puede no ser la misma utilidad que `curl` de GNU; para evitar confusiones usa `curl.exe` si está instalado o usa `Invoke-RestMethod`/`Invoke-WebRequest`. Ejemplo con `curl.exe` (si existe):

```powershell
& curl.exe -X POST "http://127.0.0.1:8000/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=martin&password=123456"
```

---

## 2) Imagen — subir archivo (image path)

Endpoint: `POST /v1/process/image`

Descripción: envía un archivo local con multipart/form-data. Importante: si envías `file` no envíes `url`.

Ejemplo curl (bash) — subir archivo y guardar resultado en `out.jpg`:

```bash
curl -s -X POST "http://127.0.0.1:8000/v1/process/image" \
  -H "Authorization: Bearer $TOKEN" \
  -F "user=martin" \
  -F "id=123" \
  -F "file=@/full/path/to/image.jpg;type=image/jpeg" \
  -F "mode=blur" \
  -F "expand=10" \
  -F "blur_strength=55" \
  -F "pixel_size=10" \
  -F "cut=false" \
  --output out.jpg
```

Notas y explicación de cada parte:
- `-F "file=@/ruta/archivo.jpg;type=image/jpeg"`: adjunta el archivo. `@` indica subida desde disco; `type=` fuerza el mime-type (útil en Windows o si curl no lo detecta).
- `-F "user=martin"` y `-F "id=123"`: campos requeridos por la API.
- `mode`, `expand`, `blur_strength`, `pixel_size` y `cut`: parámetros opcionales que modifican el comportamiento del censor.
- `--output out.jpg` guarda la respuesta binaria (image/jpeg) en el fichero `out.jpg`.

Ejemplo PowerShell usando `curl.exe` (si está disponible):

```powershell
& curl.exe -s -X POST "http://127.0.0.1:8000/v1/process/image" \
  -H "Authorization: Bearer $env:TOKEN" \
  -F "user=martin" \
  -F "id=123" \
  -F "file=@C:\\ruta\\a\\imagen.jpg;type=image/jpeg" \
  -F "mode=blur" \
  -F "expand=10" \
  -F "blur_strength=55" \
  -F "pixel_size=10" \
  -F "cut=false" -o out.jpg
```

Importante: `file` y `url` son mutuamente excluyentes: si envías `file` no envíes `url`.

---

## 3) Imagen — enviar URL (image url)

Descripción: en vez de subir un archivo, envía un `url` público que la API descargará/leerá.

Ejemplo curl (bash):

```bash
curl -s -X POST "http://127.0.0.1:8000/v1/process/image" \
  -H "Authorization: Bearer $TOKEN" \
  -F "user=martin" \
  -F "id=456" \
  -F "url=https://example.com/path/to/image.jpg" \
  -F "mode=pixelate" \
  -F "expand=8" \
  -F "cut=true" \
  --output out_from_url.jpg
```

Notas:
- El servidor hará la petición HTTP a la `url` que le des. Asegúrate de que la imagen sea públicamente accesible y que la URL sea directa a la imagen (no a una página HTML).

---

## 4) Video — subir archivo (video path)

Endpoint: `POST /v1/process/video`

Descripción: sube un archivo de video en multipart/form-data. El comportamiento y parámetros son idénticos a `/v1/process/image`, salvo que la respuesta será un `video/mp4`.

Ejemplo curl (bash) — subir archivo y guardar `out.mp4`:

```bash
curl -s -X POST "http://127.0.0.1:8000/v1/process/video" \
  -H "Authorization: Bearer $TOKEN" \
  -F "user=martin" \
  -F "id=789" \
  -F "file=@/full/path/to/video.mp4;type=video/mp4" \
  -F "mode=blur" \
  -F "expand=12" \
  -F "blur_strength=60" \
  -F "pixel_size=8" \
  -F "cut=false" \
  --output out.mp4
```

Consejos:
- Si el archivo es grande, `curl` enviará en streaming; asegúrate de tener suficiente tiempo/timeout en el servidor.

---

## 5) Video — enviar URL (video url)

Descripción: envía un campo `url` con la dirección pública del video que el servidor debe procesar.

Ejemplo curl (bash):

```bash
curl -s -X POST "http://127.0.0.1:8000/v1/process/video" \
  -H "Authorization: Bearer $TOKEN" \
  -F "user=martin" \
  -F "id=789" \
  -F "url=https://example.com/path/to/video.mp4" \
  -F "mode=blur" \
  -F "expand=10" \
  -F "blur_strength=55" \
  -F "pixel_size=10" \
  -F "cut=true" \
  --output out_from_url.mp4
```

---

## Ejemplos avanzados y debug

- Verificar cabeceras y respuesta completa: añade `-v` o `-i` a `curl`.
- Mostrar progreso durante la subida (útil para archivos grandes): elimina `-s` y usa `--progress-bar`.
- Si obtienes errores 401: asegúrate de usar `Authorization: Bearer <token>` y que el token no esté caducado.

### Extra: ejemplo completo desde 0 (bash)

```bash
# 1) Obtener token
TOKEN=$(curl -s -X POST "http://127.0.0.1:8000/auth/login" -H "Content-Type: application/x-www-form-urlencoded" -d "username=martin&password=123456" | jq -r '.access_token')

# 2) Subir imagen
curl -v -X POST "http://127.0.0.1:8000/v1/process/image" \
  -H "Authorization: Bearer $TOKEN" \
  -F "user=martin" \
  -F "id=123" \
  -F "file=@/full/path/to/image.jpg;type=image/jpeg" \
  -F "mode=blur" \
  --output result.jpg
```

---

Si quieres que adapte los ejemplos a rutas reales de tu equipo (paths de Windows), o que genere ejemplos con `Invoke-RestMethod`/`Invoke-WebRequest` para PowerShell nativo, dímelo y los añado.

Fin del documento.
