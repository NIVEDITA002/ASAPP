import streamlit as st
import requests
import PyPDF2
import speech_recognition as sr

# Function to extract text from PDF and audio
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    return text

# Authentication Functions
def register_user(email, password):
    response = requests.post("http://127.0.0.1:5000/api/register", json={
        "email": email,
        "password": password
    })
    return response.json()

def login_user(email, password):
    response = requests.post("http://127.0.0.1:5000/api/login", json={
        "email": email,
        "password": password
    })
    return response.json()

def logout_user():
    response = requests.post("http://127.0.0.1:5000/api/logout")
    return response.json()

# Streamlit UI
st.set_page_config(page_title="Hallucination Detection App", page_icon="🧠", layout="wide")

# Custom CSS for a better appearance
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f0f5;
    }
    .stButton>button {
        background-color: #4CAF50;  /* Green */
        color: white;
        border: None;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧠 Hallucination Detection Application")

# Check if user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Login and Registration section
if not st.session_state.logged_in:
    st.header("Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        result = login_user(login_email, login_password)
        if "Login successful" in result.get("message", ""):
            st.session_state.logged_in = True
            st.session_state.user_email = login_email
            st.success(result["message"])
        else:
            st.error(result.get("error", "Login failed."))
    
    st.header("Register")
    reg_email = st.text_input("Email (for registration)")
    reg_password = st.text_input("Password (for registration)", type="password")
    
    if st.button("Register"):
        result = register_user(reg_email, reg_password)
        if "User registered successfully." in result.get("message", ""):
            st.success(result["message"])
        else:
            st.error(result.get("error", "Registration failed."))

else:
    # Main application for hallucination detection
    st.success(f"Welcome, {st.session_state.user_email}!")

    # File upload and detection section
    st.header("Upload Conversation and Summary")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Conversation Text")
        conversation_text = st.text_area("Enter conversational text here:", height=150)
        uploaded_conversation_file = st.file_uploader("Or upload conversation text (TXT, PDF, or audio files)", type=["txt", "pdf", "wav", "mp3"])

    with col2:
        st.subheader("Summary Text")
        summary_text = st.text_area("Enter summary text here:", height=150)
        uploaded_summary_file = st.file_uploader("Or upload summary text (TXT, PDF, or audio files)", type=["txt", "pdf", "wav", "mp3"])

    if st.button("Check for Hallucinations"):
        # Check if conversation text is empty and extract from file if needed
        if not conversation_text and uploaded_conversation_file is not None:
            if uploaded_conversation_file.type == "text/plain":  # Handle TXT files
                conversation_text = uploaded_conversation_file.read().decode("utf-8")
            elif uploaded_conversation_file.type == "application/pdf":  # Handle PDF files
                conversation_text = extract_text_from_pdf(uploaded_conversation_file)
            elif uploaded_conversation_file.type in ["audio/wav", "audio/mpeg"]:  # Handle audio files
                conversation_text = extract_text_from_audio(uploaded_conversation_file)
            else:
                st.warning("Unsupported conversation file format!")

        # Check if summary text is empty and extract from file if needed
        if not summary_text and uploaded_summary_file is not None:
            if uploaded_summary_file.type == "text/plain":  # Handle TXT files
                summary_text = uploaded_summary_file.read().decode("utf-8")
            elif uploaded_summary_file.type == "application/pdf":  # Handle PDF files
                summary_text = extract_text_from_pdf(uploaded_summary_file)
            elif uploaded_summary_file.type in ["audio/wav", "audio/mpeg"]:  # Handle audio files
                summary_text = extract_text_from_audio(uploaded_summary_file)
            else:
                st.warning("Unsupported summary file format!")

        # Send the data to the Flask API if both texts were extracted successfully
        if conversation_text and summary_text:
            api_url = "http://127.0.0.1:5000/api/detect_hallucination"
            response = requests.post(api_url, json={
                "conversational_text": conversation_text,
                "summary": summary_text
            })

            if response.status_code == 200:
                result = response.json()
                if result['hallucination_detected']:
                    st.warning(f"Hallucination detected! (Similarity Score: {result['similarity_score']:.2f})")
                else:
                    st.success(f"No hallucination detected. (Similarity Score: {result['similarity_score']:.2f})")
            else:
                st.error("Error: Could not process the request.")
    
    if st.button("Logout"):
        logout_user()
        st.session_state.logged_in = False
        st.rerun()  # Rerun the app to show login/registration
