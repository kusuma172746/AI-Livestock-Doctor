# AI Livestock Doctor — Gemini API key in app.py

1. Open `app.py` and find `GEMINI_API_KEY = "PASTE_YOUR_NEW_GEMINI_API_KEY_HERE"` near the top.
2. Replace only the placeholder with a **new** API key from https://aistudio.google.com/apikey. Keep quotation marks.
3. In VS Code terminal run `python -m pip install -r requirements.txt` and then `python -m streamlit run app.py`.
4. Sidebar no longer asks for the API key. Photo analysis and chat still use Gemini.

**Security:** Never share `app.py` containing your real key or push it to a public GitHub repository. Revoke any previously exposed key. For public deployment, prefer environment variables or secret management.

**Safety:** Educational guidance only; not a veterinary diagnosis.
