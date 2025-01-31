import speech_recognition as sr
import pyttsx3
import spacy
import requests
from textblob import TextBlob


# Initialize recognizer and TTS engine and NLP model
recognizer = sr.Recognizer()
engine = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")

def speak_text(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def extract_entities(command):
    """Extract key entities from the command."""
    doc = nlp(command)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "GPE"]]  # Adjust to fit your needs
    return entities

def analyze_sentiment(command):
    """Analyze the sentiment of the command(optional)."""
    blob = TextBlob(command)
    return blob.sentiment.polarity

def get_department_info(department_name):
    """Fetch department info from the Flask backend."""
    url = f"http://localhost:5000/departments/{department_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Department not found"}

def get_faculty_info(faculty_name):
    """Fetch faculty info from the Flask backend."""
    url = f"http://localhost:5000/faculty/{faculty_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Faculty not found"}

def get_event_info(event_name):
    """Fetch event info from the Flask backend."""
    url = f"http://localhost:5000/events/{event_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Event not found"}

def interpret_command(command):
    """Interpret user command and return appropriate response."""
    command = command.lower()
    
    if "department" in command:
        department_name = command.split("department")[-1].strip()  # Extract department name from command
        department_info = get_department_info(department_name)
        if 'error' in department_info:
            return f"Sorry, I couldn't find information for the department {department_name}."
        else:
            return f"Here's the information for the {department_name} department: {department_info}"
    
    elif any(word in command for word in ["faculty", "professor", "teacher"]):
        faculty_name = command.split("faculty")[-1].strip()  # Extract faculty name from command
        faculty_info = get_faculty_info(faculty_name)
        if 'error' in faculty_info:
            return f"Sorry, I couldn't find information for the faculty member {faculty_name}."
        else:
            return f"Here's the information for the faculty member {faculty_name}: {faculty_info}"
    
    elif "event" in command:
        event_name = command.split("event")[-1].strip()  # Extract event name from command
        event_info = get_event_info(event_name)
        if 'error' in event_info:
            return "Sorry, I couldn't find information about the event."
        else:
            return f"Here's the information for the event: {event_info}"
    
    else:
        return "I'm not sure about that. Let me check."


def test_commands(command_list):
    for command in command_list:
        print(f"User Command: {command}")
        response = interpret_command(command)
        print(f"Response: {response}\n")

# Start voice recognition
with sr.Microphone() as source:
    print("Adjusting for ambient noise... Please wait.")
    recognizer.adjust_for_ambient_noise(source, duration=2)
    print("Listening... Speak something!")

    try:
        # Listen and process audio
        audio = recognizer.listen(source)
        print("Recognizing...")
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")

        # Respond with NLP
        response = interpret_command(command)
        print(f"Response : {response}")
        speak_text(response)

    except sr.UnknownValueError:
        print("Sorry, I couldn't understand the audio.")
        speak_text("Sorry, I couldn't understand what you said.")
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition.")
        speak_text("There seems to be an issue with the internet connection.")