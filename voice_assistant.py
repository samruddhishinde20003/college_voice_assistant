import speech_recognition as sr
import pyttsx3
import spacy
import requests

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

def clean_text_for_speech(text):
    """Remove emojis, markdown symbols, and links from the text before speaking."""
    text = re.sub(r"[\U00010000-\U0010ffff]", "", text)  # Remove emojis
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # Remove bold markdown (**bold** → bold)
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # Remove italic markdown (*italic* → italic)
    text = re.sub(r"\[.*?\]\((.*?)\)", "", text)  # Remove markdown links ([Click here](URL) → "")
    return text.strip()

def speak_text(text):
    """Convert text to speech after cleaning it for readability."""
    cleaned_text = clean_text_for_speech(text)
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
    output = f"📌 **Faculty Details:**\n"
    output += f"👤 **Name:** {faculty_info.get('name', 'N/A')}\n"
    output += f"🎓 **Designation:** {faculty_info.get('designation', 'N/A')}\n"
    output += f"🏢 **Department:** {faculty_info.get('department', 'N/A')}\n"
    specializations = ", ".join(faculty_info.get("specialization", []))
    output += f"📚 **Specialization:** {specializations if specializations else 'N/A'}\n"
    output += f"📞 **Contact:** {faculty_info.get('contact', 'N/A')}\n"
    output += f"📧 **Email:** {faculty_info.get('email', 'N/A')}\n"
    if faculty_info.get("profile_link"):
        output += f"🔗 **Profile:** [Click here]({faculty_info['profile_link']})\n"
    return output

def format_department_info(department_info):
    if "error" in department_info:
        return "Sorry, I couldn't find information for that department."
    output = f"🏛 **Department Information:**\n"
    output += f"🏢 **Name:** {department_info.get('name', 'N/A')}\n"
    output += f"📍 **Building:** {department_info.get('building', 'N/A')}\n"
    output += f"📞 **Head of Department:** {department_info.get('head', 'N/A')}\n"
    output += f"📧 **Email:** {department_info.get('email', 'N/A')}\n"
    directions = department_info.get("directions", {})
    if "text" in directions:
        output += f"🗺 **Directions:** {directions['text']}\n"
    return output

def format_event_info(events):
    if "error" in events:
        return "Sorry, no events found for this department."
    output = "🎉 **Upcoming Events:**\n"
    for event in events:
        output += f"\n📅 **Event:** {event.get('title', 'N/A')}\n"
        output += f"📖 **Description:** {event.get('description', 'N/A')}\n"
        output += f"📍 **Venue:** {event.get('venue', 'N/A')}\n"
        output += f"🕒 **Time:** {event.get('time', 'N/A')}\n"
        output += f"📞 **Organizer:** {event.get('organizer', 'N/A')}\n"
        if event.get("link"):
            output += f"🔗 **More Info:** [Click here]({event['link']})\n"
    return output

def interpret_command(command):
    command = command.lower()
    entities = extract_entities(command)
    if "event" in command or "events" in command:
        if entities["department"]:
            return format_event_info(get_event_info(entities["department"][0]))
    if entities["department"]:
        return format_department_info(get_department_info(entities["department"][0]))
    if entities["faculty"]:
        return format_faculty_info(get_faculty_info(" ".join(entities["faculty"])))
    return "🤖 I'm not sure about that. Let me check."

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
