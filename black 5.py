import streamlit as st 
import wikipedia
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
import io
import datetime
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase

# --- CONFIG ---
st.set_page_config(page_title="🧠 Enhanced Chatbot", layout="wide")

st.title("🧠 Enhanced Python Chatbot with Wikipedia, Google & Microphone")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

recognizer = sr.Recognizer()

# --- SPEECH HANDLING ---
def recognize_speech_from_browser():
    """Capture audio using browser mic with streamlit-webrtc."""
    webrtc_streamer(key="speech", mode="SENDRECV", audio_receiver_size=1024)
    st.info("🎤 Speak into your browser microphone.")
    st.warning("⚠️ Automatic speech-to-text conversion from live stream is not fully implemented here.")
    return None  # (Can be extended with real-time speech recognition)


def recognize_speech_from_upload():
    """Alternative: Upload a recorded audio file for recognition."""
    uploaded_file = st.file_uploader("Upload audio file", type=["wav", "mp3"])
    if uploaded_file:
        st.audio(uploaded_file)
        try:
            with sr.AudioFile(uploaded_file) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                return text
        except Exception as e:
            st.error(f"Error recognizing speech: {e}")
    return None

# --- CHATBOT LOGIC ---
def chatbot_response(query):
    """Simple chatbot with Wikipedia + Google fallback."""
    if not query:
        return "I didn’t catch that. Please try again."

    query = query.lower()

    # Wikipedia search
    if "wikipedia" in query:
        try:
            topic = query.replace("wikipedia", "").strip()
            return wikipedia.summary(topic, sentences=2)
        except:
            return "Sorry, I couldn’t fetch Wikipedia results."

    # Google search
    elif "search" in query or "google" in query:
        try:
            search_url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": "Mozilla/5.0"}
            page = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(page.content, "html.parser")
            result = soup.find("div", class_="BNeawe").text
            return result
        except:
            return "Sorry, I couldn’t fetch Google results."

    # Default
    else:
        return f"You said: {query}"

# --- CHAT INTERFACE ---
st.subheader("💬 Chat")

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").markdown(f"**You:** {msg['content']}")
    else:
        st.chat_message("assistant").markdown(f"**Bot:** {msg['content']}")

# Input mode
option = st.radio("Choose input mode:", ["⌨️ Text", "🌐 Browser Microphone", "📂 Upload Audio"])

user_text = None

if option == "⌨️ Text":
    user_text = st.chat_input("Type your message...")

elif option == "🌐 Browser Microphone":
    user_text = recognize_speech_from_browser()

elif option == "📂 Upload Audio":
    user_text = recognize_speech_from_upload()

# Process user input
if user_text:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # Get bot response
    bot_reply = chatbot_response(user_text)

    # Save bot reply
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    # Rerun to refresh chat
    st.experimental_rerun()
