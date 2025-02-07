const responseBox = document.getElementById("response-box");
const textInput = document.getElementById("text-input");
const submitButton = document.getElementById("submit-btn");
const micButton = document.getElementById("start-btn");

//  Function to speak response (Prevents duplicate speech)
function removeEmojis(text) {
    return text.replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ""); // Remove Unicode emojis
}

// Function to speak response (adjusting speed & removing emojis)
function speakResponse(message) {
    window.speechSynthesis.cancel();  // Stop any ongoing speech

    if (message.startsWith("You said")) return;
    let cleanedMessage = removeEmojis(message);  //  Ensure emojis are removed
    let speech = new SpeechSynthesisUtterance(cleanedMessage);
    
    speech.rate = 0.8; // Adjust speed (default is 1.0)
    
    window.speechSynthesis.speak(speech);
}


//  Function to update response box (Prevents duplicate messages)
function updateResponse(message) {
    if (!message) return; // Prevent empty messages

    const formattedMessage = message
        .replace(/🏛/g, "\n🏛")  // Department Info
        .replace(/🏢/g, "\n🏢")  // Building
        .replace(/📍/g, "\n📍")  // Location
        .replace(/📞/g, "\n📞")  // Phone Number
        .replace(/📧/g, "\n📧")  // Email
        .replace(/🗺/g, "\n🗺")  // Directions
        .replace(/📌/g, "\n📌")  // Faculty Info
        .replace(/👤/g, "\n👤")  // Faculty Name
        .replace(/🎓/g, "\n🎓")  // Faculty Designation
        .replace(/📚/g, "\n📚")  // Faculty Specialization
        .replace(/🔗/g, "\n🔗")  // Links
        .replace(/🎉/g, "\n🎉")  // Events
        .replace(/📅/g, "\n📅")  // Event Date
        .replace(/📖/g, "\n📖")  // Event Description
        .replace(/🕒/g, "\n🕒"); // Event Time

    const paragraph = document.createElement("p");
    paragraph.textContent = formattedMessage;
    paragraph.style.whiteSpace = "pre-line"; //  Ensures line breaks are respected

    responseBox.appendChild(paragraph);
    responseBox.scrollTop = responseBox.scrollHeight; // Auto-scroll
}


//  Function to handle text input
function handleTextInput() {
    const userInput = textInput.value.trim();
    if (userInput) {
        updateResponse(`You: ${userInput}`);
        eel.interpret_command(userInput)(function(response) {
            updateResponse(`Assistant: ${response}`);
            speakResponse(response); //  Speak response in JS, not Python
        });
        textInput.value = ""; // Clear input field
    } else {
        alert("Please enter a command.");
    }
}

//  Function to handle mic input
function handleMicInput() {
    updateResponse("Listening...");  //  Show "Listening..." immediately

    eel.process_voice_input()(function(response) {
        updateResponse(`Assistant: ${response}`);  //  Ensure text updates first

        //  Delay speech slightly to ensure UI is updated before speaking
        setTimeout(() => {
            speakResponse(response);
        }, 100);  // 100ms delay ensures text updates first
    });
}



//  Expose function for Python to call
eel.expose(display_response);

function display_response(message) {
    
    updateResponse(message);
    speakResponse(message); //  Speak only once
}

//  Attach event listeners
submitButton.addEventListener("click", handleTextInput);
micButton.addEventListener("click", handleMicInput);
