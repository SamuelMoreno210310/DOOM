# DOOM

Asistente personal por voz que corre en mi portátil. Lo llamo con una palabra, le hablo en español, puede abrir los documentos de una carpeta y me responde en voz alta.

Es un prototipo hecho para aprender. Funciona de punta a punta, pero todavía tiene cosas por mejorar (están al final).

## Qué hace

- Espera en silencio hasta que digo "hey jarvis".
- Convierte lo que digo en texto, sin conexión a internet para esa parte.
- Si menciono un documento de mi carpeta de trabajos, lo busca aunque no diga el nombre exacto, lo lee y lo analiza.
- Manda la pregunta a un modelo de lenguaje y recibe la respuesta.
- Dice la respuesta en voz alta.
- Tiene una ventana pequeña con un círculo que cambia de color y de tamaño según lo que esté haciendo (dormido, escuchando, pensando, hablando).

## Cómo está armado

| Parte | Herramienta |
|---|---|
| Palabra de activación | openWakeWord ("hey jarvis") |
| Voz a texto | Vosk, modelo `vosk-model-small-es-0.42` |
| Respuestas | API de NVIDIA, usada con la librería `openai` |
| Voz de salida | ElevenLabs |
| Lectura de archivos | python-docx (.docx) y lectura normal (.txt) |
| Ventana | Tkinter |

Archivos del repositorio:

- `doom.py`: primera versión, funciona por terminal.
- `doom_interfaz.py`: versión con ventana pequeña y respuestas más rápidas.
- `requirements.txt`: librerías de Python que necesita.

## Instalación (Windows)

1. Instalar Python y clonar este repositorio.
2. Instalar las librerías:

   ```
   pip install -r requirements.txt
   ```

3. Descargar el modelo de voz en español de Vosk (`vosk-model-small-es-0.42`) desde https://alphacephei.com/vosk/models y descomprimirlo dentro de `C:/DOOM`.
4. Instalar ffmpeg y dejarlo en el PATH. Sin él no se puede reproducir el audio de la respuesta.
5. Crear las claves como variables de entorno (nunca dentro del código):
   - `NVIDIA_API_KEY`
   - `ELEVENLABS_API_KEY`
6. Crear la carpeta `C:/DOOM/trabajos` y poner ahí los documentos que quiero que DOOM pueda leer.

El modelo de voz, la carpeta `trabajos` y `error.txt` están en el `.gitignore`, así que no se suben al repositorio.

## Uso

```
python doom_interfaz.py
```

1. Decir "hey jarvis" y esperar a que el círculo se ponga azul.
2. Hablar. Ejemplos: "analiza el documento del teorema del seno", "lista mis archivos".
3. Decir "salir" o cerrar la ventana para terminar.

## Limitaciones

- Las rutas (`C:/DOOM/...`) están escritas dentro del código.
- Solo lee `.docx` y `.txt`.
- El historial de la conversación se borra al cerrar el programa.
- Necesita internet y las dos claves para responder y hablar.
- La palabra de activación es "hey jarvis", no "DOOM".
- Todavía se demora entre que termino de hablar y que empieza a sonar la respuesta.

## Licencia

MIT. Ver el archivo `LICENSE`.
