import streamlit as st
from gtts import gTTS
from langdetect import detect
from deep_translator import GoogleTranslator
import tempfile
import os
from io import StringIO
from PyPDF2 import PdfReader
import base64

# ----------- Styles -----------
def apply_custom_styles():
    st.markdown("""
        <style>
            .stApp { background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            .stTextArea textarea { background-color: #2c2c2c !important; color: white !important; border: 1px solid #3b82f6; }
            .stSelectbox div[data-baseweb="select"] { background-color: #2c2c2c !important; color: white; }
            .stButton>button { background-color: #3b82f6; color: white; border-radius: 8px; padding: 0.6rem 1.2rem; font-weight: 600; transition: 0.3s; }
            .stButton>button:hover { background-color: #2563eb; }
        </style>
    """, unsafe_allow_html=True)

# ----------- Agents -----------
def suspense_agent(text):
    suspense_templates = [
        "Just when everything seemed normal, {}",
        "Little did they know, {}",
        "In the eerie silence, {}",
        "A shadow crept closer as {}",
        "With a sudden jolt, {}",
        "As tension filled the air, {}"
    ]
    sentences = text.split('.')
    suspense_text = []
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if sentence:
            template = suspense_templates[i % len(suspense_templates)]
            suspense_text.append(template.format(sentence.lower()))
    return " ".join(suspense_text)

def inspiration_agent(text):
    phrases = [
        "Believe in yourself.", "Keep moving forward.", "You're stronger than you think.",
        "Success is near.", "Push through challenges.", "Stay focused on your goals."
    ]
    sentences = text.split('.')
    result = []
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if sentence:
            result.append(f"{sentence}. {phrases[i % len(phrases)]}")
    return " ".join(result)

# ----------- File/Text Handling -----------
def extract_text(file):
    if file.type == "text/plain":
        return StringIO(file.getvalue().decode("utf-8")).read()
    elif file.type == "application/pdf":
        pdf = PdfReader(file)
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return ""

# ----------- Download Helper -----------
def get_download_link(file_path, filename="audio.mp3"):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">⬇️ Download Audio</a>'

# ----------- Language Map -----------
language_map = {
    "English": "en", "Hindi": "hi", "Spanish": "es", "French": "fr",
    "German": "de", "Italian": "it", "Chinese": "zh-CN", "Arabic": "ar"
}
language_name_map = {v: k for k, v in language_map.items()}

# ----------- Main App -----------
def main():
    apply_custom_styles()
    st.title("🗣️ EchoVerse- input-to-audio Styler & Narrator")

    with st.sidebar:
        st.header("📁 Input & Settings")
        uploaded_file = st.file_uploader("Upload .txt or .pdf", type=["txt", "pdf"])
        user_prompt = st.text_area("Or type your own content", height=180)
        style = st.selectbox("Choose Style", ["Suspense", "Inspiration", "Original", "Prompt only"])

        raw_text = ""
        if uploaded_file:
            raw_text += extract_text(uploaded_file)
        if user_prompt:
            raw_text += "\n" + user_prompt

        detected_lang_code = "en"
        if raw_text.strip():
            try:
                detected_lang_code = detect(raw_text)
                st.markdown(f"🧠 *Detected input language:* `{language_name_map.get(detected_lang_code, detected_lang_code)}`")
            except:
                st.markdown("⚠️ Language detection failed. Defaulting to English.")

        st.markdown("🌍 **Select Target Language (for translation & audio)**")
        lang_name = st.selectbox("🎧 Language to Speak", list(language_map.keys()))
        target_lang_code = language_map[lang_name]

        generate = st.button("🔊 Generate Translated Audio")

    if generate:
        if not raw_text.strip():
            st.warning("⚠️ Please upload a file or enter text.")
            return

        # Apply style
        if style == "Suspense":
            final_text = suspense_agent(raw_text)
        elif style == "Inspiration":
            final_text = inspiration_agent(raw_text)
        elif style == "Prompt only":
            final_text = user_prompt
        else:
            final_text = raw_text

        st.subheader("📄 Transformed Text (Before Translation)")
        st.write(final_text[:1500] + ("..." if len(final_text) > 1500 else ""))

        try:
            translated = GoogleTranslator(source='auto', target=target_lang_code).translate(final_text)
            st.subheader("🌐 Translated Text")
            st.write(translated[:1500] + ("..." if len(translated) > 1500 else ""))

            tts = gTTS(translated, lang=target_lang_code)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                tts.save(tmp_file.name)
                audio_path = tmp_file.name

            with open(audio_path, "rb") as audio_file:
                st.subheader("🎧 Listen to Audio")
                st.audio(audio_file.read(), format="audio/mp3")

            st.markdown(get_download_link(audio_path), unsafe_allow_html=True)

            os.remove(audio_path)
        except Exception as e:
            st.error(f"❌ Translation or Audio generation failed: {e}")

if __name__ == "__main__":
    main()
