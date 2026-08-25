// =====================================================
// ELEMENTS
// =====================================================

const chatForm = document.getElementById("chatForm");

const questionInput =
    document.getElementById("questionInput");

const chatContainer =
    document.getElementById("chatContainer");

const welcomeSection =
    document.getElementById("welcomeSection");

const sendButton =
    document.getElementById("sendButton");

const sendText =
    document.getElementById("sendText");

const loadingSpinner =
    document.getElementById("loadingSpinner");

const newConversation =
    document.getElementById("newConversation");


// =====================================================
// ADD MESSAGE TO CHAT
// =====================================================

function addMessage(role, text, metadata = null) {

    const message = document.createElement("div");

    message.className =
        `message ${role}`;


    const label =
        document.createElement("div");

    label.className =
        "message-label";

    label.textContent =
        role === "user"
            ? "You"
            : "Aster & Row";


    const bubble =
        document.createElement("div");

    bubble.className =
        "message-bubble";

    bubble.textContent =
        text;


    message.appendChild(label);

    message.appendChild(bubble);


    // -------------------------------------------------
    // Metadata
    // -------------------------------------------------

    if (
        role === "assistant" &&
        metadata
    ) {

        const metadataContainer =
            document.createElement("div");

        metadataContainer.className =
            "metadata";


        // Sources

        if (
            metadata.sources &&
            metadata.sources.length > 0
        ) {

            metadata.sources.forEach(source => {

                const tag =
                    document.createElement("span");

                tag.className =
                    "meta";

                tag.textContent =
                    `Source: ${source}`;

                metadataContainer.appendChild(tag);

            });

        }


        // Tool used

        if (metadata.tool_used === true) {

            const tag =
                document.createElement("span");

            tag.className =
                "meta success";

            tag.textContent =
                "✓ Order lookup";

            metadataContainer.appendChild(tag);

        }


        // Human handoff

        if (metadata.handoff === true) {

            const tag =
                document.createElement("span");

            tag.className =
                "meta warning";

            tag.textContent =
                "Human review recommended";

            metadataContainer.appendChild(tag);

        }


        if (
            metadata.sources &&
            metadata.sources.length === 0 &&
            metadata.tool_used !== true &&
            metadata.handoff !== true
        ) {

            const tag =
                document.createElement("span");

            tag.className =
                "meta";

            tag.textContent =
                "Grounded response";

            metadataContainer.appendChild(tag);

        }


        message.appendChild(
            metadataContainer
        );

    }


    chatContainer.appendChild(message);


    // Scroll to latest message

    message.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });

}


// =====================================================
// LOADING STATE
// =====================================================

function setLoading(isLoading) {

    sendButton.disabled =
        isLoading;

    questionInput.disabled =
        isLoading;


    if (isLoading) {

        sendText.classList.add(
            "hidden"
        );

        loadingSpinner.classList.remove(
            "hidden"
        );

    } else {

        sendText.classList.remove(
            "hidden"
        );

        loadingSpinner.classList.add(
            "hidden"
        );

        questionInput.disabled =
            false;

    }

}


// =====================================================
// ASK AGENT
// =====================================================

async function askAgent(question) {

    const response =
        await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type":
                    "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });


    const data =
        await response.json();


    if (!response.ok) {

        throw new Error(
            data.error ||
            "Something went wrong."
        );

    }


    return data;

}


// =====================================================
// FORM SUBMISSION
// =====================================================

chatForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const question =
            questionInput.value.trim();


        if (!question) {
            return;
        }


        // Hide welcome screen

        welcomeSection.style.display =
            "none";


        // Add user message

        addMessage(
            "user",
            question
        );


        // Clear input

        questionInput.value = "";


        setLoading(true);


        try {

            const result =
                await askAgent(question);


            addMessage(
                "assistant",
                result.answer,
                result
            );

        }


        catch (error) {

            addMessage(
                "assistant",
                "I'm sorry, but I couldn't process that request right now."
            );

            console.error(error);

        }


        finally {

            setLoading(false);

            questionInput.focus();

        }

    }
);


// =====================================================
// SUGGESTED QUESTIONS
// =====================================================

document
    .querySelectorAll(".suggestion")
    .forEach(button => {

        button.addEventListener(
            "click",
            function () {

                const question =
                    button.dataset.question;


                questionInput.value =
                    question;


                questionInput.focus();

            }
        );

    });


// =====================================================
// NEW CONVERSATION
// =====================================================

newConversation.addEventListener(
    "click",
    async function () {

        try {

            await fetch(
                "/reset",
                {
                    method: "POST"
                }
            );

        }

        catch (error) {

            console.error(
                "Reset failed:",
                error
            );

        }


        chatContainer.innerHTML =
            "";

        welcomeSection.style.display =
            "";

        questionInput.value =
            "";

        questionInput.focus();

    }
);


// =====================================================
// ENTER TO SEND
// SHIFT + ENTER = NEW LINE
// =====================================================

questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            chatForm.requestSubmit();

        }

    }
);