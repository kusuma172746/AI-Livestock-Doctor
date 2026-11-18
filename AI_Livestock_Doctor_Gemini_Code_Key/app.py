"""AI Livestock Doctor — educational animal-care information assistant.
Run: streamlit run app.py
"""
from io import BytesIO

import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError
from google import genai

# Paste your NEW Gemini API key here. Never share code containing a real key.
GEMINI_API_KEY = "AQ.Ab8RN6Ic2iua2NF8n9biSJKvNmyJoN76KeeTgvEf7I9h6CFJlA"
GEMINI_MODEL = "gemini-2.5-flash"

st.set_page_config(page_title="AI Livestock Doctor", page_icon="🐄", layout="wide")

# Load matching high-contrast CSS from a separate editable file.
from pathlib import Path
CSS = (Path(__file__).resolve().parent / "styles.css").read_text(encoding="utf-8")
st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🐄 AI Livestock Doctor</h1><p>Smart Animal Health Monitoring & Advisory System · Educational Prototype</p></div>', unsafe_allow_html=True)

TEXT = {
    "English": {
        "warning": "⚠️ This app provides general educational information, NOT a veterinary diagnosis. For severe symptoms, injury, breathing trouble, poisoning, or an animal that cannot stand, contact a veterinarian urgently.",
        "sidebar": "Settings", "api": "Gemini API key", "model": "Model name", "language": "Response language",
        "tabs": ["📷 Image Analysis", "💬 Animal-Care Assistant", "🌿 Care Tips", "ℹ️ About"],
        "upload": "Upload an animal photo (JPG, JPEG, PNG)", "animal": "Animal type",
        "description": "Symptoms or observations (optional)", "analyze": "Analyze Image",
        "chat": "Ask a question about animal health or care", "chat_placeholder": "e.g., My cow is not eating. What should I check?",
        "clear": "Clear chat", "key_missing": "Paste your Gemini API key into GEMINI_API_KEY near the top of app.py.",
        "photo_missing": "Upload a photo first.", "limit": "Please upload an image smaller than 10 MB.",
        "response": "AI guidance", "about": "Built with Python, Streamlit, Pillow, and the Google Gemini API. Images and questions are sent to Gemini when you request an AI response.",
    },
    "తెలుగు": {
        "warning": "⚠️ ఈ యాప్ సాధారణ అవగాహన కోసం మాత్రమే. ఇది పశువైద్యుని నిర్ధారణ కాదు. తీవ్ర లక్షణాలు, గాయం లేదా శ్వాస సమస్య ఉంటే వెంటనే పశువైద్యుని సంప్రదించండి.",
        "sidebar": "సెట్టింగ్స్", "api": "Gemini API కీ", "model": "మోడల్ పేరు", "language": "సమాధాన భాష",
        "tabs": ["📷 ఫోటో విశ్లేషణ", "💬 పశు సంరక్షణ సహాయకుడు", "🌿 సంరక్షణ సూచనలు", "ℹ️ వివరాలు"],
        "upload": "పశువు ఫోటో అప్‌లోడ్ చేయండి (JPG, JPEG, PNG)", "animal": "పశువు రకం",
        "description": "లక్షణాలు / గమనించిన విషయాలు (ఐచ్ఛికం)", "analyze": "ఫోటో విశ్లేషించు",
        "chat": "పశు ఆరోగ్యం లేదా సంరక్షణపై ప్రశ్న అడగండి", "chat_placeholder": "ఉదా: మా ఆవు మేత తినడం లేదు. ఏం చేయాలి?",
        "clear": "చాట్ తొలగించు", "key_missing": "app.py లో GEMINI_API_KEY వద్ద మీ API కీ ఇవ్వండి.",
        "photo_missing": "ముందుగా ఫోటో అప్‌లోడ్ చేయండి.", "limit": "10 MB కంటే చిన్న ఫోటో ఇవ్వండి.",
        "response": "AI సూచనలు", "about": "Python, Streamlit, Pillow మరియు Google Gemini API తో రూపొందించబడింది. మీరు AI ను ఉపయోగించినప్పుడు ఫోటో, ప్రశ్న Gemini సేవకు పంపబడతాయి.",
    },
}

with st.sidebar:
    language = st.selectbox("Response language / సమాధాన భాష", list(TEXT), key="language")
    t = TEXT[language]
    api_key = GEMINI_API_KEY.strip()
    model = GEMINI_MODEL

SYSTEM = """You are an educational livestock-care information assistant supporting cattle, buffalo,
sheep, goats and other farm animals. Do not claim to be a licensed veterinarian. Do not
provide definitive diagnosis from text or photos. State that appearance alone cannot
confirm diseases. Describe observations conservatively. Give practical low-risk care steps
(clean water, safe shelter, isolation when contagious disease is suspected) and specify
when a vet should be called, including red flags. Do not prescribe medication dosages,
antibiotics or invasive procedures. If information is missing, ask focused questions.
Never invent test results, measurements or certainty. When useful, explain that a
physical veterinary examination or lab test may be required.
"""

def call_gemini(prompt: str, image: Image.Image | None = None) -> str:
    if not api_key.strip() or api_key == "PASTE_YOUR_NEW_GEMINI_API_KEY_HERE":
        raise ValueError(t["key_missing"])
    if not model.strip():
        raise ValueError("Please enter a Gemini model name.")
    client = genai.Client(api_key=api_key.strip())
    lang_directive = "Respond entirely in Telugu (తెలుగు)." if language == "తెలుగు" else "Respond in clear, simple English."
    content = [SYSTEM + "\n" + lang_directive + "\n\nUSER REQUEST:\n" + prompt]
    if image is not None:
        content.append(image)
    result = client.models.generate_content(model=model.strip(), contents=content)
    answer = result.text
    if not answer or not answer.strip():
        raise RuntimeError("No text was returned. Try again with a clearer question or another supported model.")
    return answer.strip()


def show_error(error: Exception) -> None:
    message = str(error)
    if "API_KEY_INVALID" in message or "API key not valid" in message:
        st.error("Invalid API key. Copy a valid Gemini API key from Google AI Studio.")
    elif "429" in message or "RESOURCE_EXHAUSTED" in message:
        st.error("API quota or rate limit reached. Please check your Gemini account quota and try later.")
    elif "404" in message or "NOT_FOUND" in message:
        st.error("Model not available for your API account. Try a supported model name in Settings.")
    else:
        st.error(f"Request could not be completed: {message[:400]}")


def safe_image(file) -> Image.Image:
    raw = file.getvalue()
    if len(raw) > 10 * 1024 * 1024:
        raise ValueError(t["limit"])
    im = Image.open(BytesIO(raw))
    im.verify()
    im = Image.open(BytesIO(raw))
    im = ImageOps.exif_transpose(im).convert("RGB")
    if max(im.size) > 1600:
        im.thumbnail((1600, 1600))
    return im

image_tab, chat_tab, tips_tab, about_tab = st.tabs(t["tabs"])
with image_tab:
    st.subheader("📷 " + ("Animal Image Analysis" if language == "English" else "పశువు ఫోటో విశ్లేషణ"))
    left, right = st.columns([1, 1], gap="large")
    with left:
        uploaded = st.file_uploader(t["upload"], type=["jpg", "jpeg", "png"], key="animal_photo")
        species = st.selectbox(t["animal"], ["Cow", "Buffalo", "Goat", "Sheep", "Other"])
        observations = st.text_area(t["description"], height=110,
                                    placeholder="Example: skin irritation, not eating, swelling...")
        submit_image = st.button(t["analyze"], type="primary", use_container_width=True)
    with right:
        photo = None
        if uploaded:
            try:
                photo = safe_image(uploaded)
                st.image(photo, caption="Uploaded animal image", use_container_width=True)
            except (UnidentifiedImageError, OSError, ValueError) as exc:
                st.error(str(exc))
        else:
            st.info("Upload a clear photo in good lighting. Include relevant observations.")
    if submit_image:
        if photo is None:
            st.warning(t["photo_missing"])
        elif not api_key or api_key == "PASTE_YOUR_NEW_GEMINI_API_KEY_HERE":
            st.warning(t["key_missing"])
        else:
            prompt = (f"Animal type (user-reported): {species}. Observations: {observations or 'None given'}. "
                      "Carefully describe visible findings, possible non-definitive explanations, "
                      "safe immediate care, information to collect, and clear signs to seek urgent "
                      "veterinary attention. Do not assert a disease diagnosis from the picture.")
            with st.spinner("Analyzing with Gemini..."):
                try:
                    response = call_gemini(prompt, photo)
                    st.session_state["last_analysis"] = response
                except Exception as exc:
                    show_error(exc)
    if "last_analysis" in st.session_state:
        st.subheader(t["response"])
        st.markdown(st.session_state["last_analysis"])
        st.download_button("Download guidance", st.session_state["last_analysis"],
                           file_name="animal_guidance.txt", mime="text/plain")

with chat_tab:
    st.subheader("💬 " + ("Animal-Care Assistant" if language == "English" else "పశు సంరక్షణ సహాయకుడు"))
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if st.button(t["clear"], key="clear_chat"):
        st.session_state.messages = []
        st.rerun()
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_question = st.chat_input(t["chat_placeholder"])
    if user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        with st.chat_message("assistant"):
            if not api_key or api_key == "PASTE_YOUR_NEW_GEMINI_API_KEY_HERE":
                st.warning(t["key_missing"])
            else:
                recent_history = st.session_state.messages[-8:]
                context = "\n".join(f'{msg["role"]}: {msg["content"]}' for msg in recent_history)
                with st.spinner("Generating guidance..."):
                    try:
                        response = call_gemini("Animal-care conversation:\n" + context +
                                               "\nAnswer the most recent user question appropriately.")
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as exc:
                        show_error(exc)

with tips_tab:
    st.subheader("🌿 " + ("General Animal-Care Tips" if language == "English" else "సాధారణ పశు సంరక్షణ సూచనలు"))
    if language == "English":
        tips = {
            "💧 Clean water": "Provide fresh, clean drinking water and monitor for sudden changes in drinking habits.",
            "🥬 Appropriate feed": "Provide species-appropriate, balanced nutrition and avoid moldy feed.",
            "🏡 Clean shelter": "Keep animal housing dry, ventilated, clean, and protected from weather extremes.",
            "👀 Daily observation": "Look out for changes in appetite, behavior, movement, breathing, and manure.",
            "🩺 Veterinary care": "Consult a qualified veterinarian for vaccinations, parasite control, suspected illness, and emergencies.",
            "🧼 Hygiene": "Wash hands and equipment; separate visibly sick animals when safe and follow local veterinary advice.",
        }
    else:
        tips = {
            "💧 శుభ్రమైన నీరు": "పశువులకు ప్రతిరోజూ శుభ్రమైన తాగునీరు అందించండి.",
            "🥬 సరైన ఆహారం": "పశువు రకానికి తగిన పోషకాహారం ఇవ్వండి; పాడైన మేత ఇవ్వవద్దు.",
            "🏡 శుభ్రమైన నివాసం": "పశువుల షెడ్‌ను శుభ్రంగా, పొడిగా, గాలి వచ్చేలా ఉంచండి.",
            "👀 రోజువారీ పరిశీలన": "ఆకలి, ప్రవర్తన, నడక, శ్వాసలో మార్పులను గమనించండి.",
            "🩺 పశువైద్య సేవలు": "టీకాలు, అనారోగ్యం, అత్యవసర పరిస్థితుల కోసం పశువైద్యుని సంప్రదించండి.",
            "🧼 పరిశుభ్రత": "చేతులు, పరికరాలను శుభ్రపరచండి; అనారోగ్య పశువుల విషయంలో వైద్యుని సలహా పాటించండి.",
        }
    for title, body in tips.items():
        with st.expander(title, expanded=True):
            st.write(body)

with about_tab:
    st.subheader("ℹ️ About this project")
    st.write(t["about"])
    st.markdown("**Features:** Animal photo upload, Gemini AI guidance, animal-care Q&A, English/Telugu responses, and general care tips.")
    st.markdown("**Important limitations:** This prototype does not measure vital signs, use real-time sensors, establish confirmed diseases, or replace veterinary care.")
    st.markdown("**Privacy:** Only upload photos you have permission to share. Uploaded photos and chat questions are sent to the Gemini service when you request analysis or answers.")