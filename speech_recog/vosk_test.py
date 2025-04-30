from vosk import Model, KaldiRecognizer #reconhecer e transcrever o áudio.
import pyaudio #pyaudio: Captura áudio do microfone em tempo real.
import json
import time

# Configurar Vosk
model = Model("model-pt") 
rec = KaldiRecognizer(model, 16000) #Configura o reconhecedor com taxa de amostragem 16.000 Hz 

#captura de audio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                input=True, frames_per_buffer=4096)
stream.start_stream() #comecar captura de som 

#input=True: Habilita a captura de áudio.
#frames_per_buffer: Tamanho do buffer de captura.


print("Diga: fraco, medio ou forte...")

try:
    while True:
        data = stream.read(4096)
        
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            texto = result["text"]
            print("Você disse:", texto)

            if "fraco" in texto:
                print("Modo: FRACO (30%)")

            elif "médio" in texto:
                print("Modo: MÉDIO (60%)")
                
            elif "forte" in texto:
                print("Modo: FORTE (100%)")

except KeyboardInterrupt:
    print("Encerrando...")