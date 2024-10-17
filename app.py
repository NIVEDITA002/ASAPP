from flask import Flask, request, jsonify, session
from sentence_transformers import SentenceTransformer, util
import PyPDF2
import io
import speech_recognition as sr
from db import init_db, register_user, login_user

app = Flask(__name__)
app.secret_key = '090564f3c22f412d3b4294107f1a0242'  # Change this to a random secret key for session management

# Initialize the database
init_db()

# Load a pre-trained model for semantic similarity
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Existing text extraction and hallucination detection functions...
# (No changes here)


def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)  # Read the entire audio file
    text = recognizer.recognize_google(audio)  # You can change this to a different service if needed
    return text

def detect_hallucination(conversational_text, summary_text, threshold=0.7):
    conversation_embedding = model.encode(conversational_text, convert_to_tensor=True)
    summary_embedding = model.encode(summary_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(conversation_embedding, summary_embedding).item()
    hallucination_detected = similarity < threshold
    return hallucination_detected, similarity

@app.route('/api/detect_hallucination', methods=['POST'])
def detect_hallucination_api():
    data = request.json
    conversation = data.get('conversational_text')
    summary = data.get('summary')

    if not conversation or not summary:
        return jsonify({"error": "Both conversation and summary are required"}), 400

    hallucination, similarity = detect_hallucination(conversation, summary)

    return jsonify({
        "hallucination_detected": hallucination,
        "similarity_score": similarity
    })


@app.route('/api/register', methods=['POST'])
def register_api():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
    
    if register_user(email, password):
        return jsonify({"message": "User registered successfully."}), 201
    else:
        return jsonify({"error": "Email already exists."}), 409

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
    
    if login_user(email, password):
        session['user'] = email  # Store user in session
        return jsonify({"message": "Login successful."}), 200
    else:
        return jsonify({"error": "Invalid email or password."}), 401

@app.route('/api/logout', methods=['POST'])
def logout_api():
    session.pop('user', None)  # Remove user from session
    return jsonify({"message": "Logout successful."}), 200

if __name__ == '__main__':
    app.run(debug=True)