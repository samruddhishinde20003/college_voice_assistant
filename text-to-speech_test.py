import speech_recognition as sr
import pyttsx3
import spacy
import requests

# Initialize recognizer, TTS engine, and NLP model
recognizer = sr.Recognizer()
engine = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")

# ✅ Department mapping for consistent abbreviations
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

# ✅ Faculty mapping for accurate retrieval
faculty_mapping = {
    "rajesh": "CSE_FAC001",
    "geeta": "CSE_FAC002",
    "yerriswamy": "CSE_FAC003",
    "gopal": "ECE_FAC001",
    "manu": "ECE_FAC002",
    "rajeshwari": "ECE_FAC003",
    "sharanabasappa": "ME_FAC001",
    "anand": "ME_FAC002",
    "veerabhadrayya": "ME_FAC003"
}

def speak_text(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def extract_entities(command):
    """Extract faculty, department, and event names from the command."""
    doc = nlp(command)

    # Extract faculty names and remove "Dr." or "Prof." if present
    faculty_names = [ent.text.lower().replace("dr. ", "").replace("prof. ", "").strip()
                     for ent in doc.ents if ent.label_ == "PERSON"]
    
    # Extract department names from predefined mapping
    department_names = [word for word in department_mapping.keys() if word in command.lower()]

    event_names = []  # Placeholder for future event extraction

    return {
        "faculty": faculty_names,
        "department": department_names,
        "event": event_names
    }

def get_department_info(department_name):
    """Fetch department info from the Flask backend."""
    department_abbr = department_mapping.get(department_name.lower(), department_name.upper())
    url = f"http://localhost:5000/departments/{department_abbr}"

    print(f"Requesting URL: {url}")  
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"Response: {response.json()}")  
        return response.json()
    else:
        print(f"Error: {response.status_code}")  
        return {"error": "Department not found"}

def get_faculty_info(faculty_name):
    faculty_name = faculty_name.lower().strip()  # Normalize input
    
    # Remove common prefixes like "Dr." or "Prof." if present
    faculty_name = faculty_name.replace("dr. ", "").replace("prof. ", "").strip()

    # Look for a match in faculty_mapping (even partial match)
    for key in faculty_mapping.keys():
        if key in faculty_name:
            faculty_id = faculty_mapping[key]
            url = f"http://localhost:5000/faculty/{faculty_id}"
            print(f"Requesting faculty URL: {url}")

            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Faculty not found"}
    
    return {"error": f"Faculty {faculty_name} not found"}

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
    entities = extract_entities(command)

    # ✅ Department Queries
    if entities["department"]:
        department_name = entities["department"][0]  
        print(f"Looking up department: {department_name}")
        department_info = get_department_info(department_name)
        return f"Here's the information for the {department_name} department: {department_info}" if 'error' not in department_info else f"Sorry, I couldn't find information for {department_name}."

    # ✅ Faculty Queries
    elif entities["faculty"]:
        faculty_name = " ".join(entities["faculty"])  # Get full faculty name
        print(f"Looking up faculty: {faculty_name}")
        faculty_info = get_faculty_info(faculty_name)
        return f"Here's the information for {faculty_name}: {faculty_info}" if 'error' not in faculty_info else f"Sorry, I couldn't find information for {faculty_name}."

    # ✅ Event Queries
    elif entities["event"]:
        event_name = entities["event"][0]  
        print(f"Looking up event: {event_name}")
        event_info = get_event_info(event_name)
        return f"Here's the event information: {event_info}" if 'error' not in event_info else "Sorry, I couldn't find details for the event."

    else:
        return "I'm not sure about that. Let me check."

# 🔹 **Allow User to Input Text or Speak**
def get_user_input():
    """Allow user to either enter text manually or use voice input."""
    choice = input("Type '1' for text input or '2' for voice input: ").strip()
    
    if choice == '1':
        return input("Enter your query: ").strip()

    else:
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Listening... Speak something!")

            try:
                audio = recognizer.listen(source)
                print("Recognizing...")
                command = recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command

            except sr.UnknownValueError:
                print("Sorry, I couldn't understand the audio.")
                speak_text("Sorry, I couldn't understand what you said.")
                return None
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition.")
                speak_text("There seems to be an issue with the internet connection.")
                return None

# 🔹 **Main Program**
if __name__ == "__main__":
    command = get_user_input()
    if command:
        response = interpret_command(command)
        print(f"Response: {response}")
        speak_text(response)
