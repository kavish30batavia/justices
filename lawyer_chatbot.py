from flask import Flask, render_template, request, jsonify
import json
import re
from textblob import TextBlob
from rapidfuzz import fuzz
from rapidfuzz.process import extractOne
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from transformers import pipeline

app = Flask(__name__)

# Load law-related JSON data
def load_law_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading legal data: {e}")
        return []

# Fix spelling errors using fuzzy matching and TextBlob
def correct_spelling(text):
    words = text.split()
    corrected_words = []
    for word in words:
        best_match, score, _ = extractOne(word, LEGAL_TERMS, scorer=fuzz.WRatio)
        if score > 80:
            corrected_words.append(best_match)
        else:
            corrected_words.append(str(TextBlob(word).correct()))
    return " ".join(corrected_words)

# Fix missing spaces in "article40" → "article 40"
def fix_missing_spaces(user_input):
    return re.sub(r'(?i)(article|section)(\d+)', r'\1 \2', user_input)

# Search function with fuzzy matching
def search_related_sections(query):
    query_lower = query.lower()
    matching_entries = []

    for entry in law_data:
        title = entry.get('title', '') or entry.get('title', '')
        description = entry.get('description', '') or entry.get('description', '')

        # Use fuzzy matching to find relevant sections/articles
        title_score = fuzz.WRatio(query_lower, title.lower())
        desc_score = fuzz.WRatio(query_lower, description.lower())

        if title_score > 60 or desc_score > 60:
            category = "Article" if 'title' in entry else "Section"
            number = entry.get('article', entry.get('section', ''))
            matching_entries.append(f"{category} {number} - {title}:\n{description}")

    return "\n\n".join(matching_entries) if matching_entries else "No relevant legal references found."

# Extract article/section number from user input
def extract_number_and_category(user_input):
    match = re.search(r'(?i)(article|section)\s*(\d+)', user_input)
    return (int(match.group(2)), match.group(1).lower()) if match else (None, None)

# Get details by article/section number
def get_details_by_number(number, category):
    category = category.lower()  # Normalize input category
    print(number)
    print(category)
    for entry in law_data:
        entry_category = "article" if "article" in entry else "section"  # Identify category
        entry_number = entry.get("article", entry.get("section", ""))  # Get number
        
        if entry_category.lower() == category and str(entry_number).lower() == str(number).lower():
            title_key = "title" if category == "article" else "title"
            desc_key = "description" if category == "article" else "description"
            return f"{category.capitalize()} {number} - {entry.get(title_key, 'No Title')}:\n{entry.get(desc_key, 'No Description')}"
    
    return f"No details found for {category.capitalize()} {number}."


# Process user input and generate response
def process_input(user_text):
    if not user_text:
        return "Please enter a query before sending."

    # Fix spelling and missing spaces

    user_text = fix_missing_spaces(correct_spelling(user_text))

    # Check for article/section number
    number, category = extract_number_and_category(user_text)
    if number:
        response = get_details_by_number(number, category)
 
    else:
        response = search_related_sections(user_text)

    # Show response or "Enter Correctly" message
    if not response.strip() or response == "No relevant legal references found.":
        response = "Not Available. Please enter a valid article or section."

    return response

# Save chat as PDF
def save_as_pdf(chat_content):
    if not chat_content:
        return "No chat content to save."

    try:
        pdf_filename = os.path.join(os.getcwd(), "legal_chat.pdf")
        c = canvas.Canvas(pdf_filename, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", 12)

        y_position = height - 50

        for line in chat_content.split("\n"):
            if y_position < 50:
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = height - 50
            
            c.drawString(50, y_position, line)
            y_position -= 20

        c.save()
        return f"Chat saved successfully as:\n{pdf_filename}"
    except Exception as e:
        return f"Failed to save PDF: {str(e)}"
    




@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Legal Chatbot</title>
        <link rel="icon" href="img/logo1.jpg" type="image/jpg">
        <style>
            /* General Styles */
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-image: url('images/background.jpg'); /* Replace with your background image URL */
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                color: #FFFFFF;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }

            .dropdown {
                position: relative;
                display: inline-block;
            }
            .dropdown-content {
                display: none;
                position: absolute;
                background-color: #ac8733;
                min-width: 150px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                z-index: 1;
                text-align: left;
            }
            .dropdown-content a {
                color: rgb(236, 232, 232);
                padding: 10px;
                display: block;
                text-decoration: none;
                font-size: 16px;
            }
            .dropdown-content a:hover {
                background-color: #f9a826;
                color: white;
            }
            .dropdown:hover .dropdown-content {
                display: block;
            }
            nav {
                background: #4a2c02;
                padding: 15px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                display: flex;
                justify-content: center;
                align-items: center;
                position: relative;
            }
            .menu {
                display: flex;
                justify-content: center;
            }
            .menu a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-size: 18px;
                transition: color 0.3s;
            }
            .menu a:hover {
                color: #f9a826;
            }

            /* Main Content */
            .container {
                background-color: rgba(61, 40, 3, 0.9); /* Semi-transparent dark blue */
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                width: 1000px;
                padding: 20px;
                margin: 10px auto;
                flex: 1;
            }

            .header {
                display: flex;
                align-items: center;
                margin-bottom: 40px;
            }

            .header .logo {
                font-size: 24px;
                margin-right: 10px;
            }

            .header .title {
                font-size: 18px;
                font-weight: bold;
            }

            .chat-display {
                background-color: #F0F0F0;
                color: #333333;
                height: 300px;
                padding: 10px;
                border-radius: 5px;
                overflow-y: auto;
                margin-bottom: 20px;
            }

            .entry-frame {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }

            #user-input {
                flex: 1;
                padding: 10px;
                border: 2px solid #FFA07A;
                border-radius: 5px;
                font-size: 14px;
            }

            #send-button {
                background-color: #FFA07A;
                color: #FFFFFF;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }

            .actions {
                display: flex;
                gap: 10px;
            }

            #copy-button, #pdf-button, #clear-button {
                background-color: #FFD700;
                color: #1E3A5F;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }

            /* Information Section */
            .info-section {
                background-color: rgba(61, 40, 3, 0.9); /* Semi-transparent dark blue */
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                width: 1000px;
                padding: 20px;
                margin: 20px auto;
                color: #FFFFFF;
            }

            .info-section h2 {
                font-size: 20px;
                margin-bottom: 15px;
                text-align: center;
            }

            .info-section ul {
                list-style-type: disc;
                padding-left: 20px;
            }

            .info-section li {
                margin-bottom: 10px;
                font-size: 14px;
            }
footer {
    background:#4a2c02;
    color: white;
    text-align: center;
    padding: 40px 20px 10px;
    font-size: 14px;
}

/* Footer Container */
.footer-container {
    background:#4a2c02 ;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    max-width: 1200px;
    margin: auto;
    gap: 20px;
    padding: 20px;
}

/* Footer Sections */
.footer-section {
    flex: 1;
    min-width: 250px;
    margin: 10px;
    text-align: left;
}

/* Section Titles */
.footer-section h3 {
    color: #f9a826;
    margin-bottom: 15px;
    font-size: 18px;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 2px solid #f9a826;
    padding-bottom: 5px;
    display: inline-block;
}

/* Footer Links */
.footer-links ul {
    list-style: none;
    padding: 0;
}

.footer-links ul li {
    margin: 10px 0;
}

.footer-links ul li a {
    color: #f9a826;
    text-decoration: none;
    font-size: 16px;
    transition: color 0.3s, transform 0.3s;
}

.footer-links ul li a:hover {
    color: white;
    transform: translateX(5px);
}

/* Contact Section */
.footer-contact p {
    margin: 8px 0;
    font-size: 16px;
}

.footer-contact a {
    color: #f9a826;
    text-decoration: none;
    font-weight: bold;
}

.footer-contact a:hover {
    color: white;
}

/* Social Media Icons */
.social-icons {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 10px;
    margin-top: 10px;
}

.social-icons a {
    display: inline-block;
    width: 40px;
    height: 40px;
}

.social-icons img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
    transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
}

.social-icons img:hover {
    transform: scale(1.2);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

/* Footer Bottom */


/* Responsive Footer */
@media (max-width: 768px) {
    .footer-container {
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    .footer-section {
        min-width: unset;
        text-align: center;
    }

    .social-icons {
        justify-content: center;
    }
}
/* Judiciary Links Section */
.footer-courts {
    text-align: left;
}

.footer-courts ul {
    list-style: none;
    padding: 0;
}

.footer-courts ul li {
    margin: 10px 0;
}

.footer-courts ul li a {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #f9a826;
    text-decoration: none;
    font-size: 16px;
    transition: color 0.3s, transform 0.3s;
}

.footer-courts ul li a:hover {
    color: white;
    transform: translateX(5px);
}

/* Icons for Court Links */
.footer-courts ul li a::before {

    font-size: 18px;
}
        </style>
    </head>
    <body>
        <!-- Navigation Bar -->
        <nav>
            <div class="menu">
                <a href="index.html">Home</a>
               <a href="def about()">About</a>
            

                <div class="dropdown">
                 <a href="/service.html">Services</a>
                    <div class="dropdown-content">
                        <a href="/chatbot.html">Chatbot</a>
                    <a href="http://127.0.0.1:5000">Section Chatbot</a>
                        <a href="C:/Users/lenovo/Desktop/project/index.html">Case Reference</a>
                        <a href="file:///C:/Users/lenovo/Desktop/project/lawyerside/lawerreg.html">Constitution of India</a>
                        <a href="earn.html">Earn</a>
                    </div>
                </div>
                <a href="help.html">Help</a>
            </div>
        </nav>

        <!-- Main Content -->
        <div class="container">
            <div class="header">
                <div class="logo">⚖️</div>
                <div class="title">Legal Chatbot</div>
            </div>
            <div class="chat-display" id="chat-display"></div>
            <div class="entry-frame">
                <input type="text" id="user-input" placeholder="Type your message..." />
                <button id="send-button">➤</button>
            </div>
            <div class="actions">
                <button id="copy-button">Copy Chat</button>
                <button id="pdf-button">Save as PDF</button>
                <button id="clear-button">Clear Chat</button>
                <button id="summary-button">Summary</button>
            </div>
        </div>

        <!-- Information Section -->
        <div class="info-section">
            <h2>What Information Can the Chatbot Provide?</h2>
            <ul>
                <li>Legal advice on property disputes.</li>
                <li>Guidance on criminal law and procedures.</li>
                <li>Information about family law, including divorce and custody.</li>
                <li>Details about labor and employment laws.</li>
                <li>Assistance with contract law and agreements.</li>
            </ul>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>&copy; 2023 Legal Chatbot. All rights reserved. | <a href="#">Privacy Policy</a></p>
        </div>
        <footer>
        <nav>
            <div class="footer-container">
                <div class="footer-section footer-links">
                    <h3>Quick Links</h3>
                    <ul>
                        <li><a href="index.html">🏠 Home</a></li>
                        <li><a href="about.html">ℹ️ About</a></li>
                        <li><a href="service.html">💼 Services</a></li>
                        <li><a href="chatbot.html">🤖 Chatbot</a></li>
                        <li><a href="http://127.0.0.1:5000">📌 Section Chatbot</a></li>
                        <li><a href="case_reference.html">📜 Case Reference</a></li>
                        <li><a href="consitution_of_india.html">📖 Constitution of India</a></li>
                        <li><a href="help.html">❓ Help</a></li>
                    </ul>
                </div>
                <div class="footer-section footer-courts">
                    <h3>Judiciary Links</h3>
                    <ul>
                        <li><a href="https://www.sci.gov.in/" target="_blank">⚖️ Supreme Court of India</a></li>
                        <li><a href="https://bombayhighcourt.nic.in/" target="_blank">🏛️ High Courts of India</a></li>
                    </ul>
                </div>
                <div class="footer-section footer-contact">
                    <h3>Contact Us</h3>
                    <p>📧 Email: <a href="mailto:finalyearprojectlaw@gmail.com">finalyearprojectlaw@gmail.com</a></p>
                    <p>📞 Phone: +91 98765 43210</p>
                    <p>📍 Address: Mumbai, India</p>
                </div>
        
                <div class="footer-section footer-social">
                    <h3>Follow Us</h3>
                    <div class="social-icons">
                        <a href="https://www.facebook.com/" target="_blank">
                            <img src="facebook.png" alt="Facebook">
                        </a>
                        <a href="https://www.instagram.com/" target="_blank">
                            <img src="instagram.jpeg" alt="Instagram">
                        </a>
                        <a href="https://www.linkedin.com/" target="_blank">
                            <img src="linkedin.png" alt="LinkedIn">
                        </a>
                    </div>
                </div>
            </div>
        
            
    </nav>
        <p>&copy; 2025 Law Chatbot Help | All Rights Reserved</p>
    </footer>

        <script>
            document.addEventListener("DOMContentLoaded", () => {
                const chatDisplay = document.getElementById("chat-display");
                const userInput = document.getElementById("user-input");
                const sendButton = document.getElementById("send-button");
                const copyButton = document.getElementById("copy-button");
                const pdfButton = document.getElementById("pdf-button");
                const clearButton = document.getElementById("clear-button");

                // Function to add a message to the chat display
                function addMessage(message, isUser = false) {
                    const messageElement = document.createElement("div");
                    messageElement.className = isUser ? "user-message" : "bot-message";
                    messageElement.textContent = isUser ? `You: ${message}` : `Bot: ${message}`;
                    chatDisplay.appendChild(messageElement);
                    chatDisplay.scrollTop = chatDisplay.scrollHeight; // Auto-scroll
                }

                // Function to send a message to the backend
                async function sendMessage() {
                    const userMessage = userInput.value.trim();
                    if (!userMessage) return;

                    addMessage(userMessage, true);
                    userInput.value = "";

                    try {
                        const response = await fetch('/process', {
                            method: "POST",
                            headers: { "Content-Type": "application/x-www-form-urlencoded" },
                            body: `user_input=${encodeURIComponent(userMessage)}`
                        });
                        const data = await response.json();
                        addMessage(data.response);
                    } catch (error) {
                        addMessage("Error: Failed to connect to the server.");
                    }
                }

                // Function to clear the chat display
                function clearChat() {
                    chatDisplay.innerHTML = ""; // Clear all messages
                }

                // Event listeners
                sendButton.addEventListener("click", sendMessage);
                userInput.addEventListener("keypress", (e) => {
                    if (e.key === "Enter") sendMessage();
                });

                // Copy chat content
                copyButton.addEventListener("click", () => {
                    const chatContent = chatDisplay.textContent;
                    navigator.clipboard.writeText(chatContent).then(() => {
                        alert("Chat copied to clipboard!");
                    });
                });

                // Save chat as PDF
                pdfButton.addEventListener("click", () => {
                    const { jsPDF } = window.jspdf;
                    const doc = new jsPDF();
                    const chatContent = chatDisplay.textContent;
                    doc.text(chatContent, 10, 10);
                    doc.save("chatbot_conversation.pdf");
                });

                // Clear chat
                clearButton.addEventListener("click", clearChat);
            });
        </script>
    </body>
    </html>
    '''

@app.route('/process', methods=['POST'])
def process():
    user_text = request.form['user_input']
    response = process_input(user_text)
    return jsonify({'response': response})
@app.route('/about.html')
def about():
    return render_template('about.html')

@app.route('/save_pdf', methods=['POST'])
def save_pdf():
    chat_content = request.form['chat_content']
    result = save_as_pdf(chat_content)
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)