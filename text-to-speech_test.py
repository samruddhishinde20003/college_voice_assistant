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
    """Extract faculty, department, and event names from the command."""
    doc = nlp(command)
    
    faculty_names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]  # Extract faculty names
    department_names = [word for word in department_mapping.keys() if word in command.lower()]  # Extract departments
    event_names = [ent.text for ent in doc.ents if ent.label_ in ["EVENT"]]  # Extract events

    return {
        "faculty": faculty_names,
        "department": department_names,
        "event": event_names
    }


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

def interpret_command(command):
    """Interpret user command and return appropriate response."""
    command = command.lower()

    # Extract entities
    entities = extract_entities(command)

    # Check for department queries
    if entities["department"]:
        department_name = entities["department"][0]  # First detected department
        print(f"Looking up department: {department_name}")
        department_info = get_department_info(department_name)
        return f"Here's the information for the {department_name} department: {department_info}" if 'error' not in department_info else f"Sorry, I couldn't find information for {department_name}."

    # Check for faculty queries
    elif entities["faculty"]:
        faculty_name = entities["faculty"][0]  # First detected faculty
        print(f"Looking up faculty: {faculty_name}")
        faculty_info = get_faculty_info(faculty_name)
        return f"Here's the information for {faculty_name}: {faculty_info}" if 'error' not in faculty_info else f"Sorry, I couldn't find information for {faculty_name}."

    # Check for event queries
    elif entities["event"]:
        event_name = entities["event"][0]  # First detected event
        print(f"Looking up event: {event_name}")
        event_info = get_event_info(event_name)
        return f"Here's the event information: {event_info}" if 'error' not in event_info else "Sorry, I couldn't find details for the event."

    else:
        return "I'm not sure about that. Let me check."



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

    # Extract entities
    entities = extract_entities(command)

    # Check for department queries
    if entities["department"]:
        department_name = entities["department"][0]  # First detected department
        print(f"Looking up department: {department_name}")
        department_info = get_department_info(department_name)
        return f"Here's the information for the {department_name} department: {department_info}" if 'error' not in department_info else f"Sorry, I couldn't find information for {department_name}."

    # Check for faculty queries
    elif entities["faculty"]:
        faculty_name = entities["faculty"][0]  # First detected faculty
        print(f"Looking up faculty: {faculty_name}")
        faculty_info = get_faculty_info(faculty_name)
        return f"Here's the information for {faculty_name}: {faculty_info}" if 'error' not in faculty_info else f"Sorry, I couldn't find information for {faculty_name}."

    # Check for event queries
    elif entities["event"]:
        event_name = entities["event"][0]  # First detected event
        print(f"Looking up event: {event_name}")
        event_info = get_event_info(event_name)
        return f"Here's the event information: {event_info}" if 'error' not in event_info else "Sorry, I couldn't find details for the event."

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
