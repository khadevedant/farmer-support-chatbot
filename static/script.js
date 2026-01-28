let selectedLanguage = "en";

document.addEventListener("DOMContentLoaded", () => {
    const langSelect = document.getElementById("languageSelect");
    langSelect.addEventListener("change", () => {
        selectedLanguage = langSelect.value;
    });

    const input = document.getElementById("userInput");
    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
});

function sendMessage() {
    let userInput = document.getElementById("userInput");
    let message = userInput.value.trim();

    if (message === "") return;

    displayMessage(message, "user-msg");
    userInput.value = "";

    fetch("/get", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, language: selectedLanguage })
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(data.reply, "bot-msg");
        maybeSpeak(data.reply);
    })
    .catch(err => {
        console.error(err);
    });
}

function displayMessage(message, type) {
    let chatbox = document.getElementById("chatbox");
    let div = document.createElement("div");
    div.className = type;
    div.innerText = message;
    chatbox.appendChild(div);
    chatbox.scrollTop = chatbox.scrollHeight;
}

// ------------------- VOICE (SPEECH → TEXT) -------------------
function startVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Speech recognition not supported in this browser.");
        return;
    }

    const recognition = new SpeechRecognition();

    if (selectedLanguage === "hi") {
        recognition.lang = "hi-IN";
    } else if (selectedLanguage === "mr") {
        // Marathi support may be limited, fallback to Hindi/English if needed
        recognition.lang = "mr-IN";
    } else {
        recognition.lang = "en-IN";
    }

    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("userInput").value = transcript;
        sendMessage();
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
    };

    recognition.start();
}

// ------------------- VOICE (TEXT → SPEECH) -------------------
function maybeSpeak(text) {
    const ttsToggle = document.getElementById("ttsToggle");
    if (!ttsToggle.checked) return;

    if (!("speechSynthesis" in window)) return;

    const utter = new SpeechSynthesisUtterance(text);

    if (selectedLanguage === "hi") {
        utter.lang = "hi-IN";
    } else if (selectedLanguage === "mr") {
        utter.lang = "mr-IN"; // may fallback to hi-IN if not available
    } else {
        utter.lang = "en-IN";
    }

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
}
