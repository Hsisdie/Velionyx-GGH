import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.title("ASHA Scribe")

audio_file = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a", "ogg"])

if st.button("Test Gemini"):
    if not audio_file:
        st.error("Please upload an audio file first.")
    else:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            client = genai.Client(api_key=api_key)
            model_name = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
            
            audio_bytes = audio_file.read()
            mime_type = audio_file.type or "audio/wav"
            
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type
            )
            
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    audio_part,
                    "Write a faithful transcript of this audio in its original language."
                ]
            )
            st.write(response.text)
        except Exception as e:
            st.error(str(e))
