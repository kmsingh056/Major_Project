import streamlit as st
from PIL import Image
import pytesseract
from googletrans import Translator
from gtts import gTTS
import os
import magic
import tempfile
import speech_recognition as sr

# Set Tesseract path if needed (Windows example)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize translator
translator = Translator()

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Streamlit UI
st.title("OCR, Translation, and Text-to-Speech App")

# Input: Target Language
target_language = st.text_input("Enter the target language code (e.g., 'fr' for French, 'es' for Spanish):")

# Input: Image or Audio File
uploaded_file = st.file_uploader("Upload an image or audio file", type=["jpg", "png", "jpeg", "wav", "mp3"])

if uploaded_file is not None:
    file_details = {"filename": uploaded_file.name, "filetype": uploaded_file.type, "filesize": uploaded_file.size}
    st.write(file_details)

    # Check if the file is an image or audio
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(uploaded_file.read(1024))
    uploaded_file.seek(0)  # Reset file pointer

    if file_type.startswith('image'):
        # Process image with OCR
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        extracted_text = pytesseract.image_to_string(image)
        st.write("Extracted Text:")
        st.write(extracted_text)

        if target_language:
            # Translate the extracted text
            translated = translator.translate(extracted_text, dest=target_language)
            st.write("Translated Text:")
            st.write(translated.text)

            # Convert translated text to speech
            tts = gTTS(translated.text, lang=target_language)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name, format='audio/mp3')
                os.unlink(fp.name)  # Delete the temporary file after playing

    elif file_type.startswith('audio'):
        # Process audio file with Speech-to-Text
        st.write("Processing audio file...")

        # Save the uploaded audio file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_audio_file:
            tmp_audio_file.write(uploaded_file.read())
            tmp_audio_path = tmp_audio_file.name

        # Use SpeechRecognition to convert audio to text
        with sr.AudioFile(tmp_audio_path) as source:
            audio = recognizer.record(source)  # Read the entire audio file
            try:
                extracted_text = recognizer.recognize_google(audio)  # Use Google Web Speech API
                st.write("Extracted Text from Audio:")
                st.write(extracted_text)

                if target_language:
                    # Translate the extracted text
                    translated = translator.translate(extracted_text, dest=target_language)
                    st.write("Translated Text:")
                    st.write(translated.text)

                    # Convert translated text to speech
                    tts = gTTS(translated.text, lang=target_language)
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                        tts.save(fp.name)
                        st.audio(fp.name, format='audio/mp3')
                        os.unlink(fp.name)  # Delete the temporary file after playing
            except sr.UnknownValueError:
                st.error("Google Web Speech API could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Web Speech API; {e}")

        # Delete the temporary audio file
        os.unlink(tmp_audio_path)

    else:
        st.write("Unsupported file type. Please upload an image or audio file.")