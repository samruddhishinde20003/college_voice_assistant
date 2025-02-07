import speech_recognition as sr
import pyttsx3
import spacy
import requests
import eel

# Initialize recognizer, TTS engine, and NLP model
recognizer = sr.Recognizer()
engine = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")

# Department mapping for consistent abbreviations
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

# Faculty mapping for accurate retrieval
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

import re
import emoji

def clean_text_for_speech(text):
    """Remove emojis, markdown symbols, and links from the text before speaking."""
    text = emoji.replace_emoji(text, replace='')  # Remove emojis using emoji library
    text = re.sub(r"[^\w\s,.!?]", "", text)  # Extra step to remove any special symbols

    #  Remove Markdown formatting
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Remove bold markdown (**bold** → bold)
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # Remove italic markdown (*italic* → italic)

    #  Remove links
    text = re.sub(r"\[.*?\]\((.*?)\)", "", text)  # Remove markdown links ([Click here](URL) → "")

    return text.strip()

def speak_text(text):
    """Convert text to speech after removing emojis and formatting issues."""
    cleaned_text = clean_text_for_speech(text)  #  Remove emojis
    
    engine.setProperty('rate', 180)  #  Adjust speech speed
    
    print(f" Raw Text: {text}")  
    print(f" Cleaned Text: {cleaned_text}")  # Debugging

    engine.say(cleaned_text)
    engine.runAndWait()

def extract_entities(command):
    """Extract faculty, department, and event names from the command."""
    doc = nlp(command)
    faculty_names = [
        ent.text.lower().replace("dr.", "").replace("prof.", "").replace("mam", "").replace("sir", "").strip()
        for ent in doc.ents if ent.label_ == "PERSON"
    ]
    for key in faculty_mapping.keys():
        if key in command.lower():
            faculty_names.append(key)
    faculty_names = list(set(faculty_names))
    department_names = [word for word in department_mapping.keys() if word in command.lower()]
    return {"faculty": faculty_names, "department": department_names, "event": []}

def get_department_info(department_name):
    """Fetch department info from the Flask backend."""
    department_abbr = department_mapping.get(department_name.lower(), department_name.upper())
    url = f"http://localhost:5000/departments/{department_abbr}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "Department not found"}

def get_faculty_info(faculty_name):
    faculty_name = faculty_name.lower().replace("dr ", "").replace("prof ", "").replace("mam", "").replace("sir", "").replace(".", "").strip()
    for key in faculty_mapping.keys():
        if faculty_name in key.lower() or key.lower() in faculty_name:
            faculty_id = faculty_mapping[key]
            url = f"http://localhost:5000/faculty/{faculty_id}"
            response = requests.get(url)
            return response.json() if response.status_code == 200 else {"error": "Faculty not found"}
    return {"error": f"Faculty {faculty_name} not found"}

def get_event_info(department_name):
    """Fetch event info from the Flask backend."""
    url = f"http://localhost:5000/events/{department_name}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {"error": "No events found for this department"}

def format_faculty_info(faculty_info):
    if "error" in faculty_info:
        return "Sorry, I couldn't find information for that faculty member."
    output = f"📌 Faculty Details:\n"
    output += f"👤 Name: {faculty_info.get('name', 'N/A')}\n"
    output += f"🎓 Designation: {faculty_info.get('designation', 'N/A')}\n"
    output += f"🏢 Department: {faculty_info.get('department', 'N/A')}\n"
    specializations = ", ".join(faculty_info.get("specialization", []))
    output += f"📚 Specialization: {specializations if specializations else 'N/A'}\n"
    output += f"📞 Contact: {faculty_info.get('contact', 'N/A')}\n"
    output += f"📧 Email: {faculty_info.get('email', 'N/A')}\n"
    if faculty_info.get("profile_link"):
        output += f"🔗 Profile: [Click here]({faculty_info['profile_link']})\n"
    return output

def format_department_info(department_info):
    if "error" in department_info:
        return "Sorry, I couldn't find information for that department."
    output = f"🏛 Department Information:\n"
    output += f"🏢 Name: {department_info.get('name', 'N/A')}\n"
    output += f"📍 Building: {department_info.get('building', 'N/A')}\n"
    output += f"📞 Head of Department: {department_info.get('head', 'N/A')}\n"
    output += f"📧 Email: {department_info.get('email', 'N/A')}\n"
    directions = department_info.get("directions", {})
    if "text" in directions:
        output += f"🗺 Directions: {directions['text']}\n"
    return output

def format_event_info(events):
    if "error" in events:
        return "Sorry, no events found for this department."
    output = "🎉 Upcoming Events:\n"
    for event in events:
        output += f"\n📅 Event: {event.get('title', 'N/A')}\n"
        output += f"📖 Description: {event.get('description', 'N/A')}\n"
        output += f"📍 Venue: {event.get('venue', 'N/A')}\n"
        output += f"🕒 Time: {event.get('time', 'N/A')}\n"
        output += f"📞 Organizer: {event.get('organizer', 'N/A')}\n"
        if event.get("link"):
            output += f"🔗 More Info: [Click here]({event['link']})\n"
    return output
from textblob import TextBlob  #  Import TextBlob for sentiment analysis

def analyze_sentiment(command):
    """Analyze the sentiment of the user's input using TextBlob."""
    sentiment = TextBlob(command).sentiment.polarity  # Get sentiment polarity (-1 to 1)
    
    if sentiment > 0.2:
        return "😊 You seem happy! How can I assist you today?"
    elif sentiment < -0.2:
        return "😟 You sound a bit down. Is there anything I can help with?"
    else:
        return "Hello! How can I assist you?"
    
@eel.expose
def interpret_command(command):
    """Interpret user command and return structured response."""
    command = command.lower()

    #  Handle greetings separately
    if command in ["hello", "hi", "hey"]:
        return analyze_sentiment(command)
    
    entities = extract_entities(command)

    if "event" in command or "events" in command:
        if entities["department"]:
            department_name = entities["department"][0]
            event_info = get_event_info(department_name)
            response = format_event_info(event_info)
            cleaned_response = clean_text_for_speech(response)  #  Ensure text is cleaned
            eel.displayResponse(cleaned_response) 
            #speak_text(response)  #  Speak response
            return response

    if entities["department"]:
        department_name = entities["department"][0]
        department_info = get_department_info(department_name)
        response = format_department_info(department_info)
        cleaned_response = clean_text_for_speech(response)  #  Ensure text is cleaned
        eel.displayResponse(cleaned_response) 
        #speak_text(response)  #  Speak response
        return response

    if entities["faculty"]:
        faculty_name = " ".join(entities["faculty"])
        faculty_info = get_faculty_info(faculty_name)
        response = format_faculty_info(faculty_info)
        cleaned_response = clean_text_for_speech(response)  #  Ensure text is cleaned
        eel.displayResponse(cleaned_response) 
        #speak_text(response)  #  Speak response
        return response

    #speak_text("I'm not sure about that. Let me check.")
    return "🤖 I'm not sure about that. Let me check."


# 🔹 *Allow User to Input Text or Speak*

@eel.expose
def process_text_input(user_input):
    """Process text input from the frontend."""
    response = interpret_command(user_input)
    print(f"Response: {response}")
    speak_text(response)
    eel.display_response(response)  # Send response back to frontend

@eel.expose
def process_voice_input():
    """Capture voice input and process it."""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Listening...")
            audio = recognizer.listen(source)
        
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        
        eel.display_response(f"You said: {command}")
        response = interpret_command(command)
        speak_text(response)
        eel.display_response(response)  # Send response to frontend
    except sr.UnknownValueError:
        eel.display_response("Sorry, I couldn't understand that.")
    except sr.RequestError:
        eel.display_response("Couldn't reach the Google API.")


@eel.expose
def main(command):
    """Process the command from the frontend and respond accordingly."""
    if command:
        response = interpret_command(command)
        print(f"Response: {response}")  # Debugging
        
        eel.display_response(response)  #  Send response to frontend
        speak_text(response)  #  Speak only once



eel.init('Jarvis-main')
eel.start('index.html', size=(800, 600), port=8001)