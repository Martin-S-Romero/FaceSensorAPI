import cv2
import mediapipe as mp
import numpy as np
import requests
import tempfile
import os

class FaceCensor:
    def __init__(self, mode="blur", blur_strength=55, expand=10, pixel_size=10, cut=False):
        """
        Crea una instancia de FaceCensor.

        Parámetros:
            mode: str -> tipo de censura ("blur", "black" o "pixelate")
            blur_strength: int -> intensidad del desenfoque (para modo blur)
            expand: int -> expansión del área de censura alrededor de ojos/boca (y del recorte si cut=True)
            pixel_size: int -> tamaño del píxel (para modo pixelate)
            cut: bool -> si True, recorta la imagen final al área de la cara detectada (cara completa)
        """
        self.mode = mode
        self.blur_strength = blur_strength
        self.expand = expand
        self.pixel_size = pixel_size
        self.cut = cut

        # Inicializa MediaPipe FaceMesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Índices de landmarks relevantes para censura puntual
        self.LEFT_EYE = [33, 133]
        self.RIGHT_EYE = [362, 263]
        self.MOUTH = [78, 308, 14, 13]

    def _resolve_path(self, path):
        """
        Acepta ruta local o URL.
        Si es URL, descarga el archivo a un archivo temporal y devuelve su path local.
        """
        if path.startswith("http://") or path.startswith("https://"):
            try:
                print(f"🌐 Descargando archivo desde URL: {path}")
                response = requests.get(path, timeout=10)
                response.raise_for_status()

                # -----------------------------
                # 1. Extraer extensión limpia
                # -----------------------------
                clean_url = path.split("?")[0]  # eliminar parámetros
                _, ext = os.path.splitext(clean_url)

                # Si no hay extensión válida, asumimos jpg
                if ext.lower() not in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]:
                    ext = ".jpg"

                # -----------------------------
                # 2. Crear archivo temporal sin caracteres ilegales
                # -----------------------------
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                temp_file.write(response.content)
                temp_file.close()

                print(f"📥 Archivo descargado temporalmente en: {temp_file.name}")
                return temp_file.name

            except Exception as e:
                print(f"❌ Error al descargar archivo desde URL: {e}")
                return None

        # Si es ruta local
        return path

    def _ensure_output_path(self, output_path):
        """
        Crea automáticamente todas las carpetas necesarias para la ruta indicada.
        """
        folder = os.path.dirname(output_path)
        if folder and not os.path.exists(folder):
            try:
                os.makedirs(folder, exist_ok=True)
                print(f"📁 Carpeta creada: {folder}")
            except Exception as e:
                print(f"❌ Error creando carpeta de salida: {e}")

    def _validate_resolution(self, width, height, min_width=1280, min_height=720):
        """
        Verifica si la resolución del contenido es suficiente para procesar.
        Por defecto requiere al menos HD (1280x720).
        """
        width = int(width)
        height = int(height)

        if width < min_width or height < min_height:
            print(f"⚠️ Advertencia: resolución demasiado baja ({width}x{height}). "
                f"Se requiere al menos {min_width}x{min_height} para procesar correctamente.")
            return False
        else:
            print(f"✅ Resolución válida: {width}x{height}")
            return True

    def _get_box(self, points):
        """Devuelve las coordenadas del rectángulo que encierra los puntos."""
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
        return min(x_coords), min(y_coords), max(x_coords), max(y_coords)

    def _apply_censor(self, image, points):
        """Aplica el tipo de censura seleccionado sobre el área correspondiente.
           Devuelve (image_modificada, (x1,y1,x2,y2) o None si no hay región)."""
        x1, y1, x2, y2 = self._get_box(points)

        # Expande el área censurada según el parámetro "expand"
        x1 = max(x1 - self.expand, 0)
        y1 = max(y1 - self.expand, 0)
        x2 = min(x2 + self.expand, image.shape[1])
        y2 = min(y2 + self.expand, image.shape[0])

        roi = image[y1:y2, x1:x2]
        if roi.size == 0:
            return image, None

        # Aplica el tipo de censura elegido
        if self.mode == "blur":
            # blur_strength debe ser impar y razonablemente grande
            k = self.blur_strength if self.blur_strength % 2 == 1 else self.blur_strength + 1
            roi = cv2.GaussianBlur(roi, (k, k), 30)

        elif self.mode == "black":
            roi[:] = (0, 0, 0)

        elif self.mode == "pixelate":
            h, w = roi.shape[:2]
            # evita pixel_size > min(h,w)
            px = max(1, min(self.pixel_size, min(h, w)))
            roi_small = cv2.resize(roi, (px, px), interpolation=cv2.INTER_LINEAR)
            roi = cv2.resize(roi_small, (w, h), interpolation=cv2.INTER_NEAREST)

        image[y1:y2, x1:x2] = roi
        return image, (x1, y1, x2, y2)

    def _process_frame(self, frame):
        """Procesa un frame y aplica censura en los ojos y la boca.
           Si cut=True, recorta la imagen a la caja de la cara completa (usando todos los landmarks)."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return frame

        h, w, _ = frame.shape
        final_box = None

        for face_landmarks in results.multi_face_landmarks:
            # Lista con todos los puntos del rostro (x,y)
            landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in face_landmarks.landmark]

            # 1) Determinar caja completa de la cara usando todos los landmarks
            fx1, fy1, fx2, fy2 = self._get_box(landmarks)
            # expandir la caja de la cara completa con el mismo parámetro expand
            fx1 = max(fx1 - self.expand, 0)
            fy1 = max(fy1 - self.expand, 0)
            fx2 = min(fx2 + self.expand, frame.shape[1])
            fy2 = min(fy2 + self.expand, frame.shape[0])
            final_box = (fx1, fy1, fx2, fy2)

            # 2) Aplicar censura puntual (ojos y boca)
            frame, _ = self._apply_censor(frame, [landmarks[i] for i in self.LEFT_EYE])
            frame, _ = self._apply_censor(frame, [landmarks[i] for i in self.RIGHT_EYE])
            frame, _ = self._apply_censor(frame, [landmarks[i] for i in self.MOUTH])

            # Si quisieras censurar más zonas, agrégalas aquí

            # (usamos max_num_faces=1 por defecto; si hay más caras podrías guardar varias cajas)
            break  # quitamos break si quieres procesar múltiples caras individualmente

        # 3) Si se pide recortar, recortamos con la caja de la cara completa
        if self.cut and final_box:
            x1, y1, x2, y2 = final_box
            # Aseguramos enteros y límites válidos
            x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
            # Evitar recorte vacío
            if x2 > x1 and y2 > y1:
                frame = frame[y1:y2, x1:x2]

        return frame

    def run(self):
        """Inicia la cámara y aplica la censura en tiempo real."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ No se pudo acceder a la cámara.")
            return

        print(f"🎥 Cámara iniciada | Modo: {self.mode.upper()} | Expand: {self.expand}px | Cut: {self.cut} — Presiona 'ESC' para salir.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = self._process_frame(frame)
            # Si cut=True la imagen puede ser más pequeña; mostrar sin flip mantiene recorte natural
            display = cv2.flip(frame, 1)
            cv2.imshow(f"Censura facial ({self.mode})", display)

            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        print("✅ Cámara cerrada correctamente.")

    def process_image(self, input_path, output_path=None, show=True):

        """Procesa imagen desde archivo o URL."""
        # 🔥 NUEVO: Resolver URL o ruta local
        real_path = self._resolve_path(input_path)
        if real_path is None:
            print("🚫 No se pudo obtener la imagen de entrada.")
            return None

        """Procesa una imagen desde archivo aplicando la censura (y opcional recorte)."""
        image = cv2.imread(real_path)
        if image is None:
            print(f"❌ No se pudo leer la imagen: {input_path}")
            return None
        
        h, w = image.shape[:2]

        # ⚠️ Validación de resolución
        if not self._validate_resolution(w, h):
            print("🚫 Imagen descartada por baja resolución.")
            return None  # Asegura que NO continúe el procesamiento

        result = self._process_frame(image)

        if output_path:
            # Crear carpeta si no existe
            self._ensure_output_path(output_path)

            # Guardar imagen
            cv2.imwrite(output_path, result)
            print(f"💾 Imagen censurada guardada en: {output_path}")

        if show:
            cv2.imshow("Imagen censurada", result)
            print("🖼️ Presiona cualquier tecla para cerrar la imagen...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return result

    def process_video(self, input_path, output_path="output_censurado.mp4", show=True):

        """Procesa video aplicando censura desde archivo o URL."""
        
        # 🔥 NUEVO: Resolver URL o ruta local
        real_path = self._resolve_path(input_path)
        if real_path is None:
            print("🚫 No se pudo obtener el video de entrada.")
            return None

        """Procesa un video aplicando censura en cada frame.
        Si cut=True el video resultante tendrá la resolución del primer recorte válido detectado.
        """
        cap = cv2.VideoCapture(real_path)
        if not cap.isOpened():
            print(f"❌ No se pudo abrir el video: {input_path}")
            return
    
        # ⚠️ Leer el primer frame para asegurar que el tamaño sea correcto
        ret, first_frame = cap.read()
        if not ret or first_frame is None:
            print("❌ No se pudo leer el primer frame del video.")
            cap.release()
            return

        orig_h, orig_w = first_frame.shape[:2]

        # ✅ Validar resolución mínima (HD)
        if not self._validate_resolution(orig_w, orig_h):
            print(f"🚫 Video descartado por baja resolución ({orig_w}x{orig_h}).")
            cap.release()
            return

        # Volver al inicio porque ya leímos un frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # Obtener FPS (float)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 1:
            fps = 30.0

        # Dimensiones originales (fallback)
        orig_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None
        writer_size = None  # (w, h) que usará el writer

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        i = 0
        print(f"🎞️ Procesando video: {input_path}")
        print(f"💾 Guardando en: {output_path}")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            processed = self._process_frame(frame)  # puede ser recortado si cut=True

            # Determinar tamaño del frame procesado
            h_p, w_p = processed.shape[:2]

            # Si aún no inicializamos writer:
            if out is None:
                if self.cut:
                    # Si estamos en modo cut, preferimos iniciar con el primer frame recortado (si tiene cara)
                    # Si el primer processed es igual a original size, significa que no hubo recorte todavía;
                    # entonces esperamos hasta que haya un processed más pequeño (primera detección con recorte)
                    if (w_p, h_p) == (orig_w, orig_h):
                        # aún no se detectó recorte -> podemos esperar a la próxima iteración
                        # pero para no bloquear indefinidamente, si no se detecta recorte en las primeras N frames
                        # usamos el tamaño original como fallback. Aquí usamos N = 30.
                        if i < 30:
                            # No inicializar aún, continuar
                            pass
                        else:
                            writer_size = (orig_w, orig_h)
                            # Crear carpeta si no existe
                            self._ensure_output_path(output_path)
                            out = cv2.VideoWriter(output_path, fourcc, fps, writer_size)
                    else:
                        # Primer recorte válido: usamos su tamaño para el writer
                        writer_size = (w_p, h_p)
                        # Crear carpeta si no existe
                        self._ensure_output_path(output_path)
                        out = cv2.VideoWriter(output_path, fourcc, fps, writer_size)
                else:
                    # No estamos en modo cut: writer toma tamaño original del video
                    writer_size = (orig_w, orig_h)
                    # Crear carpeta si no existe
                    self._ensure_output_path(output_path)
                    out = cv2.VideoWriter(output_path, fourcc, fps, writer_size)

            # Si aún no creamos out, simplemente seguimos (esperando detección o fallback)
            if out is None:
                i += 1
                continue

            # A partir de aquí, out está inicializado: forzamos que el frame que escribimos tenga el tamaño writer_size
            target_w, target_h = writer_size

            # Si processed ya tiene la misma resolución, escribir directo
            if (w_p, h_p) == (target_w, target_h):
                frame_to_write = processed
            else:
                # Redimensionar manteniendo aspecto podría requerir padding.
                # Aquí haremos un redimensionado simple que preserva la relación de aspecto y paddings negros.
                # Calculamos escala para encajar processed dentro de writer_size
                scale = min(target_w / w_p, target_h / h_p)
                new_w = max(1, int(w_p * scale))
                new_h = max(1, int(h_p * scale))
                resized = cv2.resize(processed, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                # Crear canvas negro y centrar la imagen redimensionada
                canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
                x_offset = (target_w - new_w) // 2
                y_offset = (target_h - new_h) // 2
                canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                frame_to_write = canvas

            out.write(frame_to_write)

            if show:
                cv2.imshow("Video censurado", frame_to_write)
                if cv2.waitKey(1) & 0xFF == 27:
                    print("🛑 Procesamiento interrumpido por el usuario.")
                    break

            i += 1
            if i % 10 == 0:
                print(f"Progreso: {i}/{frame_count} frames procesados", end="\r")

        cap.release()
        if out:
            out.release()
        if show:
            cv2.destroyAllWindows()

        print(f"\n✅ Video censurado guardado correctamente en: {output_path}")
