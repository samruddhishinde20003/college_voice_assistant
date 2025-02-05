const responseBox = document.getElementById("response-box");
const textInput = document.getElementById("text-input");
const submitButton = document.getElementById("submit-btn");
const micButton = document.getElementById("start-btn");

// ✅ Function to speak response (Prevents duplicate speech)
function speakResponse(message) {
    window.speechSynthesis.cancel();  // Stop any ongoing speech
    let speech = new SpeechSynthesisUtterance(message);
    window.speechSynthesis.speak(speech);
}

// ✅ Function to update response box (Prevents duplicate messages)
function updateResponse(message) {
    if (responseBox.lastChild && responseBox.lastChild.textContent === message) {
        return; // Prevent duplicate messages
    }
    const paragraph = document.createElement("p");
    paragraph.textContent = message;
    responseBox.appendChild(paragraph);
    responseBox.scrollTop = responseBox.scrollHeight; // Auto-scroll
}

// ✅ Function to handle text input
function handleTextInput() {
    const userInput = textInput.value.trim();
    if (userInput) {
        updateResponse(`You: ${userInput}`);
        eel.interpret_command(userInput)(function(response) {
            updateResponse(`Assistant: ${response}`);
            speakResponse(response); // ✅ Speak response in JS, not Python
        });
        textInput.value = ""; // Clear input field
    } else {
        alert("Please enter a command.");
    }
}

// ✅ Function to handle mic input
function handleMicInput() {
    updateResponse("Listening...");
    eel.process_voice_input()(function(response) {
        updateResponse(`Assistant: ${response}`);
        speakResponse(response); // ✅ Speak response in JS, not Python
    });
}

// ✅ Expose function for Python to call
eel.expose(display_response);

function display_response(message) {
    updateResponse(message);
    speakResponse(message); // ✅ Speak only once
}

// ✅ Attach event listeners
submitButton.addEventListener("click", handleTextInput);
micButton.addEventListener("click", handleMicInput);
