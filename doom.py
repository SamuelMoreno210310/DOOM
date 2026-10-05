import os
import json
import queue
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
from openwakeword.model import Model as WakeModel
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play as reproducir_audio
from docx import Document

# --- Conexión con NVIDIA (reemplaza a Anthropic) ---
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY")
)

# --- Conexión con ElevenLabs (voz de salida) ---
eleven_client = ElevenLabs()  # toma la clave sola desde ELEVENLABS_API_KEY
VOICE_ID = "N2lVS1w4EtoT3dr4eOWO"  # el que ya tenías configurado

# --- Reconocimiento de voz (Vosk) ---
modelo_voz = Model("C:/DOOM/vosk-model-small-es-0.42")
cola_audio = queue.Queue()

def callback_audio(indata, frames, time, status):
    cola_audio.put(bytes(indata))

def escuchar():
    print("🎤 Habla ahora (di algo y espera un momento en silencio)...")
    reconocedor = KaldiRecognizer(modelo_voz, 16000)
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                            channels=1, callback=callback_audio):
        while True:
            data = cola_audio.get()
            if reconocedor.AcceptWaveform(data):
                resultado = json.loads(reconocedor.Result())
                texto = resultado.get("text", "")
                if texto:
                    return texto

# --- Palabra de activación (openWakeWord) ---
wake_model = WakeModel(wakeword_models=["hey_jarvis"])

def esperar_palabra_clave():
    print("😴 DOOM esperando que lo llames (di 'hey jarvis')...")
    with sd.RawInputStream(samplerate=16000, blocksize=1280, dtype='int16', channels=1) as stream:
        while True:
            audio_bytes, _ = stream.read(1280)
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
            prediccion = wake_model.predict(audio_np)
            print(prediccion["hey_jarvis"])
            if prediccion["hey_jarvis"] > 0.2:
                print("✅ Te escuché, dime.")
                return

# --- Acceso a archivos ---
CARPETA_TRABAJOS = "C:/DOOM/trabajos"

def listar_archivos():
    return os.listdir(CARPETA_TRABAJOS)

def leer_archivo(nombre):
    ruta = os.path.join(CARPETA_TRABAJOS, nombre)
    if not os.path.exists(ruta):
        return None
    if nombre.endswith(".docx"):
        doc = Document(ruta)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

   
def encontrar_archivo(mensaje):
    mensaje_l = mensaje.lower()
    archivos = listar_archivos()

    for nombre in archivos:
        if nombre.lower() in mensaje_l:
            return nombre

    mejor_nombre = None
    mejor_puntaje = 0
    for nombre in archivos:
        base = os.path.splitext(nombre)[0].lower()
        palabras = [p for p in base.replace("-", " ").replace("_", " ").split() if len(p) > 2]
        coincidencias = sum(1 for p in palabras if p in mensaje_l)
        if coincidencias > mejor_puntaje:
            mejor_puntaje = coincidencias
            mejor_nombre = nombre

    return mejor_nombre

# --- Prompt de DOOM ---
SYSTEM_PROMPT = """Eres DOOM, el asistente personal de Samuel Alejandro Moreno León, estudiante de décimo (curso 1003) que cursa TDC IB y MAI. Corres como programa en su portátil y lo ayudas con sus trabajos, tareas y proyectos.

Cómo hablas:
- Claro y directo, con palabras de un estudiante de décimo, sin tecnicismos salvo que te los pida.
- Sin frases de relleno como "Por supuesto" o "Espero que te ayude". Ve al punto.
- No exageres la importancia de las cosas ni suenes perfecto o promocional.

Fuentes e información:
- Nunca inventes fuentes, autores, cifras, citas ni enlaces.
- Si citas algo que él no conoce, dale el nombre de la fuente y el enlace. Si no puedes dar ambos, no lo cites.
- Si no sabes algo o no estás seguro, dilo.

Reglas generales:
- Cada trabajo es distinto: no asumas que es igual al anterior.
- Si te falta información, haz una sola pregunta antes de empezar."""

historial = []

print("DOOM listo. Di 'salir' para terminar.\n")

while True:
    esperar_palabra_clave()
    mensaje = escuchar()
    print("Tú (voz):", mensaje)

    if mensaje.lower() == "salir":
        break

    if "lista" in mensaje.lower() and "archivo" in mensaje.lower():
        archivos = listar_archivos()
        print("\nDOOM: Tienes estos archivos:", ", ".join(archivos), "\n")
        continue

    nombre_archivo = encontrar_archivo(mensaje)
    if nombre_archivo:
        contenido = leer_archivo(nombre_archivo)
        mensaje = f"Analiza este documento llamado {nombre_archivo}:\n\n{contenido}\n\nMi pregunta: {mensaje}"

    historial.append({"role": "user", "content": mensaje})

    respuesta = client.chat.completions.create(
        model="meta/muse-glimmer-30b",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + historial
    )

    texto_respuesta = respuesta.choices[0].message.content
    print("\nDOOM:", texto_respuesta, "\n")

    historial.append({"role": "assistant", "content": texto_respuesta})

    audio = eleven_client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=texto_respuesta,
        model_id="eleven_multilingual_v2"
    )
    reproducir_audio(audio)