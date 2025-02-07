// Ensure Eel is properly loaded before using it
eel.expose(sendUserInput);
eel.expose(displayResponse);

// Function to send user input to Python backend
function sendUserInput(userInput) {
    console.log("Sending to Python:", userInput);
    eel.interpret_command(userInput)(function(response) {
        console.log("Response from Python:", response);
        displayResponse(response);
    });
}


// Function to display assistant response in the UI
function removeEmojis(text) {
    return text.replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, ""); // Remove Unicode emojis
}

function displayResponse(message) {
    const responseBox = document.getElementById("response-box");

    let cleanedMessage = removeEmojis(message); // ✅ Remove emojis

    console.log("🔹 Raw Response from Python:", message);  
    console.log("✅ Cleaned Response for Display:", cleanedMessage);  

    if (responseBox.lastChild && responseBox.lastChild.textContent === cleanedMessage) {
        return;
    }

    const paragraph = document.createElement("p");
    paragraph.textContent = cleanedMessage;
    
    responseBox.appendChild(paragraph);
    responseBox.scrollTop = responseBox.scrollHeight; // Auto-scroll
    // ✅ Delay speech slightly to ensure UI is updated before speaking
    setTimeout(() => {
        speakResponse(cleanedMessage);
    }, 100);  // 100ms delay for UI rendering
}


// ✅ Handle text input from user
document.getElementById("submit-btn").addEventListener("click", () => {
    const userInput = document.getElementById("text-input").value.trim();
    
    if (userInput) {
        displayResponse(`You: ${userInput}`);
        sendUserInput(userInput);  // Send input to Python backend
        document.getElementById("text-input").value = "";  // Clear input field
    } else {
        alert("Please enter a command!");
    }
});

// ✅ Handle voice input when 'Start Listening' button is clicked
document.getElementById("start-btn").addEventListener("click", function () {
    displayResponse("Listening...");
    eel.main(); // ✅ Call Python function only once, without extra argument
});
