import streamlit as st
from PIL import Image
import pytesseract
from googletrans import Translator
from gtts import gTTS
import os
import magic
import tempfile

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

# Set Tesseract path if needed (Windows example)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize translator
translator = Translator()

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
        # Process audio file (placeholder for audio-to-text conversion)
        st.write("Audio file processing is not implemented in this example.")
    else:
        st.write("Unsupported file type. Please upload an image or audio file.")