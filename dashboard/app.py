from flask import Flask, render_template
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import json
import serial
import threading
import time

# =========================
# FLASK
# =========================

app = Flask(__name__)

# =========================
# SERIAL
# =========================

bano = serial.Serial('COM5', 9600)

habitacion = serial.Serial('COM6', 9600)

cocina = serial.Serial('COM7', 9600)

time.sleep(2)

# =========================
# VOSK
# =========================

model = Model("vosk-model-small-es-0.42")

recognizer = KaldiRecognizer(model, 16000)

q = queue.Queue()

# =========================
# ESTADOS
# =========================

# BAÑO

estado_bano = "APAGADO"

# HABITACION

estado_luces = "APAGADAS"

estado_persiana = "CERRADA"

# COCINA

estado_nevera = "OFF"

estado_cocina = "OFF"

estado_extractor = "OFF"

estado_luces_cocina = "OFF"

# PARQUEADERO

estado_parqueadero = "CERRADO"

# =========================
# AUDIO
# =========================

def audio_callback(indata, frames, time_info, status):

    q.put(bytes(indata))

# =========================
# VOZ
# =========================

def escuchar_voz():

    global estado_bano
    global estado_luces
    global estado_persiana

    global estado_nevera
    global estado_cocina
    global estado_extractor
    global estado_luces_cocina

    global estado_parqueadero

    print("=================================")
    print(" CASA INTELIGENTE ")
    print("=================================")
    print("Asistente de voz iniciado...")
    print("=================================")

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=audio_callback
    ):

        while True:

            data = q.get()

            if recognizer.AcceptWaveform(data):

                resultado = json.loads(
                    recognizer.Result()
                )

                texto = resultado.get(
                    "text",
                    ""
                ).lower()

                if texto != "":

                    print("\nEscuche:", texto)

                # =========================
                # BAÑO
                # =========================

                if "spa" in texto:

                    bano.write(b"spa\n")

                    estado_bano = "SPA"

                    print("Modo SPA")

                elif "mañana" in texto or "manana" in texto:

                    bano.write(b"manana\n")

                    estado_bano = "MANANA"

                    print("Modo MANANA")

                elif "noche" in texto:

                    bano.write(b"noche\n")

                    estado_bano = "NOCHE"

                    print("Modo NOCHE")

                elif texto == "apagar":

                    bano.write(b"off\n")

                    estado_bano = "APAGADO"

                    print("Sistema apagado")

                # =========================
                # HABITACION
                # =========================

                elif "encender luces" in texto:

                    habitacion.write(b"luceson\n")

                    estado_luces = "ENCENDIDAS"

                    print("Luces encendidas")

                elif "apagar luces" in texto:

                    habitacion.write(b"lucesoff\n")

                    estado_luces = "APAGADAS"

                    print("Luces apagadas")

                elif "abrir persiana" in texto:

                    habitacion.write(
                        b"abrirpersiana\n"
                    )

                    estado_persiana = "ABIERTA"

                    print("Persiana abierta")

                elif "cerrar persiana" in texto:

                    habitacion.write(
                        b"cerrarpersiana\n"
                    )

                    estado_persiana = "CERRADA"

                    print("Persiana cerrada")

                # =========================
                # PARQUEADERO
                # =========================

                elif "abrir parqueadero" in texto:

                    cocina.write(b"G_OPEN\n")

                    estado_parqueadero = "ABIERTO"

                    print("Parqueadero abierto")

                elif "cerrar parqueadero" in texto:

                    cocina.write(b"G_CLOSE\n")

                    estado_parqueadero = "CERRADO"

                    print("Parqueadero cerrado")

                # =========================
                # NEVERA
                # =========================

                elif "encender nevera" in texto:

                    cocina.write(b"N_ON\n")

                    estado_nevera = "ON"

                    print("Nevera encendida")

                elif "apagar nevera" in texto:

                    cocina.write(b"N_OFF\n")

                    estado_nevera = "OFF"

                    print("Nevera apagada")

                # =========================
                # COCINA
                # =========================

                elif "encender cocina" in texto:

                    cocina.write(b"E_ON\n")

                    estado_cocina = "ON"

                    print("Cocina encendida")

                elif "apagar cocina" in texto:

                    cocina.write(b"E_OFF\n")

                    estado_cocina = "OFF"

                    print("Cocina apagada")

                # =========================
                # EXTRACTOR
                # =========================

                elif "encender extractor" in texto:

                    cocina.write(b"EXT_ON\n")

                    estado_extractor = "ON"

                    print("Extractor encendido")

                elif "apagar extractor" in texto:

                    cocina.write(b"EXT_OFF\n")

                    estado_extractor = "OFF"

                    print("Extractor apagado")

                # =========================
                # LUCES COCINA
                # =========================

                elif "encender luces cocina" in texto:

                    cocina.write(b"L_ON\n")

                    estado_luces_cocina = "ON"

                    print("Luces cocina ON")

                elif "apagar luces cocina" in texto:

                    cocina.write(b"L_OFF\n")

                    estado_luces_cocina = "OFF"

                    print("Luces cocina OFF")

# =========================
# DASHBOARD
# =========================

@app.route('/')
def inicio():

    return render_template(

        'index.html',

        estado_bano=estado_bano,

        estado_luces=estado_luces,

        estado_persiana=estado_persiana,

        estado_nevera=estado_nevera,

        estado_cocina=estado_cocina,

        estado_extractor=estado_extractor,

        estado_luces_cocina=estado_luces_cocina,

        estado_parqueadero=estado_parqueadero
    )

# =========================
# MAIN
# =========================

if __name__ == '__main__':

    hilo_voz = threading.Thread(
        target=escuchar_voz
    )

    hilo_voz.daemon = True

    hilo_voz.start()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )