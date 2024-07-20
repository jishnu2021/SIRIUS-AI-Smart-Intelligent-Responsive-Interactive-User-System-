import pyttsx3
import speech_recognition as sr
import os
import webbrowser
from pytube import Search
from datetime import datetime
import cv2
import requests

GEMINI_API_KEY = 'Your_API_KEY'
GEMINI_API_ENDPOINT = 'https://api.gemini.com/v1/ask'

def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query

def openWebsite(command):
    site = command.replace("open ", "")
    say(f"Opening {site}")
    webbrowser.open(f"https://{site}.com")

def playMedia(command):
    media_name = command.replace("play ", "")
    

    local_media_path = f"./{media_name}.mp3"
    if os.path.isfile(local_media_path):
        say(f"Playing {media_name}")
        os.system(f'vlc "{local_media_path}"')
    else:
        
        say(f"Searching {media_name} on YouTube")
        s = Search(media_name)
        video = s.results[0]
        webbrowser.open(video.watch_url)

def tellTime():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    say(f"The current time is {current_time}")

def openCamera():
    global cap
    if cap is None or not cap.isOpened():
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                say("Camera opened. Press 'q' to close the camera window.")
                while cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        cv2.imshow('Camera', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    else:
                        say("Failed to capture video.")
                        break
            else:
                say("Failed to open camera.")
        except Exception as e:
            say(f"An error occurred: {e}")
    else:
        say("Camera is already opened.")

def clickPicture():
    global cap
    if cap is None or not cap.isOpened():
        say("Camera is not opened yet.")
    else:
        try:
            ret, frame = cap.read()
            if ret:
                filename = "picture.jpg"
                cv2.imwrite(filename, frame)
                say("Picture taken.")
            else:
                say("Failed to take picture.")
        except Exception as e:
            say(f"An error occurred: {e}")

def startVideoRecording():
    global cap, recording
    if cap is None or not cap.isOpened():
        say("Camera is not opened yet.")
    else:
        try:
            filename = "video.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
            recording = True
            say("Video recording started.")
            while recording and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    cv2.imshow('Recording', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    say("Failed to capture video.")
                    break
            out.release()
            cv2.destroyAllWindows()
            say("Video recording stopped.")
            recording = False
        except Exception as e:
            say(f"An error occurred: {e}")

def askGemini(question):
    try:
        response = requests.post(
            GEMINI_API_ENDPOINT,
            headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
            json={"question": question}
        )
        response.raise_for_status()
        answer = response.json().get('answer', 'No answer found.')
        return answer
    except Exception as e:
        print(f"An error occurred: {e}")
        return "I'm sorry, I couldn't get an answer."

cap = None
recording = False

say("Hello, I am Synthia A.I.")

while True:
    command = takeCommand().lower()
    if command == "none":
        continue
    elif "stop" in command:
        if cap:
            cap.release()
        cv2.destroyAllWindows()
        say("Goodbye!")
        break
    elif "open the camera" in command:
        openCamera()
    elif "click picture" in command:
        clickPicture()
    elif "start video" in command:
        startVideoRecording()
    elif "stop video" in command:
        if recording:
            recording = False
            if cap:
                cap.release()
            cv2.destroyAllWindows()
            say("Video recording stopped.")
        else:
            say("No video recording to stop.")
    elif "open" in command:
        openWebsite(command)
    elif "play" in command:
        playMedia(command)
    elif "time" in command or "what's the time" in command or "what is the time" in command:
        tellTime()
    elif "question" in command:
        question = command.replace("question", "").strip()
        answer = askGemini(question)
        say(answer)
    else:
        say(command)
