import speech_recognition as sr
import pyttsx3
import spacy
import requests
from textblob import TextBlob

# Initialize recognizer and TTS engine and NLP model
recognizer = sr.Recognizer()
engine = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")

# List of known departments and their mappings to abbreviations
department_mapping = {
    'cse': 'CSE', 
    'computer science': 'CSE', 
    'computer science and engineering': 'CSE',
    'ece': 'ECE', 
    'electronics and communication': 'ECE', 
    'electronics and communication engineering': 'ECE',
    'mechanical engineering': 'ME',
    'civil': 'CV', 
    'civil engineering': 'CV', 
    'eee': 'EEE', 
    'electrical and electronics engineering': 'EEE',
    'electrical and electronics': 'EEE'
}

def speak_text(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def extract_entities(command):
    """Extract key entities from the command."""
    doc = nlp(command)
    entities = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "GPE"]]  # Entities like organization or geographical locations
    return entities

def get_department_info(department_name):
    """Fetch department info from the Flask backend."""
    # Get the abbreviated department name from the mapping
    department_abbr = department_mapping.get(department_name.lower(), None)
    if department_abbr:
        url = f"http://localhost:5000/departments/{department_abbr}"
    else:
        # If no abbreviation was found, directly use the original input
        department_abbr = department_name.upper()  # Default to uppercase
        url = f"http://localhost:5000/departments/{department_abbr}"

    print(f"Requesting URL: {url}")  # Log the URL being requested
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Response: {response.json()}")  # Log the successful response
        return response.json()
    else:
        print(f"Error: {response.status_code}")  # Log the error code
        return {"error": "Department not found"}

def get_faculty_info(faculty_name):
    """Fetch faculty info from the Flask backend using name instead of _id."""
    formatted_name = faculty_name.strip()  # Ensure no spaces at the start or end
    url = f"http://localhost:5000/faculty/{formatted_name}"
    
    print(f"Requesting faculty URL: {url}")  # Debug log
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Faculty not found"}


def get_event_info(department_name):
    """Fetch event info from the Flask backend."""
    url = f"http://localhost:5000/events/{department_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "No events found for this department"}

def interpret_command(command):
    """Interpret user command and return appropriate response."""
    command = command.lower()

    # Try to match the department names with the command
    department_name = None
    for dept in department_mapping.keys():
        if dept in command:
            department_name = dept
            break

    if department_name:
        print(f"Looking up department: {department_name}")  # Log the department name
        department_info = get_department_info(department_name)
        if 'error' in department_info:
            return f"Sorry, I couldn't find information for the {department_name} department."
        else:
            return f"Here's the information for the {department_name} department: {department_info}"

    # Handle other cases (faculty, events)
    elif any(word in command for word in ["faculty", "professor", "teacher"]):
        faculty_name = command.replace("faculty", "").strip()  # Extract faculty name by removing the word "faculty"
        faculty_info = get_faculty_info(faculty_name)
        if 'error' in faculty_info:
            return f"Sorry, I couldn't find information for the faculty member {faculty_name}."
        else:
            return f"Here's the information for the faculty member {faculty_name}: {faculty_info}"

    elif "event" in command:
        department_name = command.replace("event", "").strip()  # Extract department name for events
        event_info = get_event_info(department_name)
        if 'error' in event_info:
            return "Sorry, I couldn't find information about the event."
        else:
            return f"Here's the information for the event: {event_info}"

    else:
        return "I'm not sure about that. Let me check."

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
