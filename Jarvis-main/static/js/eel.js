// Ensure Eel is properly loaded before using it
eel.expose(sendUserInput);
eel.expose(displayResponse);

// Function to send user input to Python backend
function sendUserInput(userInput) {
    eel.interpret_command(userInput)(function(response) {
        displayResponse(response);
    });
}

// Function to display assistant response in the UI
function displayResponse(message) {
    const responseBox = document.getElementById("response-box");

    // Prevent duplicate messages
    if (responseBox.lastChild && responseBox.lastChild.textContent === message) {
        return;
    }

    // Create a new paragraph element for each response
    const paragraph = document.createElement("p");
    paragraph.textContent = message;
    
    responseBox.appendChild(paragraph);
    responseBox.scrollTop = responseBox.scrollHeight; // Auto-scroll
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
