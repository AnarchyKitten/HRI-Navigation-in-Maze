import speech_recognition as sr

if __name__ == "__main__":
    r = sr.Recognizer()
    mic = sr.Microphone(device_index=0)

    while(True):

        respond = ""

        with mic as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)

        try:
            respond = r.recognize_google(audio)
        except:
            respond = ""

        if "left" in respond:
            print("Turning Left")
        elif "right" in respond:
            print("Turning Right")
        elif "ahead" in respond:
            print("go ahead")
        elif "forward" in respond:
            print("go ahead")
