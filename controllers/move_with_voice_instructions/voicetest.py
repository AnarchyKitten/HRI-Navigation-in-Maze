import threading
import speech_recognition as sr
import time

r = sr.Recognizer()
mic = sr.Microphone(device_index=0)

while(True):

        respond = ""

        print(time.time())

        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

        try:
            respond = r.recognize_google(audio)
        except:
            respond = ""

        print(respond)
        print(time.time())