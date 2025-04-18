import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import openai
import os
import tempfile

st.set_page_config(page_title="🤖 Luna – Your AI Report Assistant by Matteo", layout="wide")
st.title("🤖 Luna – Your AI Report Assistant by Matteo")

openai.api_key = st.secrets["openai_key"]

st.header("📂 Carica uno o più file (PDF, Excel, CSV, TXT)")
uploaded_files = st.file_uploader("Trascina i file qui", type=["pdf", "csv", "xlsx", "txt"], accept_multiple_files=True)

pdf_texts = []
pdf_paths = []
allegati = []

if uploaded_files:
    for file in uploaded_files:
        ext = file.name.split(".")[-1].lower()
        st.subheader(f"📎 {file.name}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
            content = file.read()
            if not content:
                st.warning(f"⚠️ Il file {file.name} è vuoto o non leggibile.")
                continue
            tmp.write(content)
            tmp_path = tmp.name
            allegati.append(tmp_path)

        if ext == "pdf":
            try:
                doc = fitz.open(tmp_path)
                text = "\n".join([page.get_text() for page in doc])
                pdf_texts.append(text)
                st.text_area("📝 Testo estratto dal PDF", text, height=200)
            except Exception as e:
                st.error(f"❌ Errore nel leggere {file.name}: {e}")

        elif ext == "csv":
            try:
                df = pd.read_csv(tmp_path)
                st.dataframe(df.head())
            except:
                st.error("❌ Impossibile leggere il CSV.")

        elif ext == "xlsx":
            try:
                df = pd.read_excel(tmp_path)
                st.dataframe(df.head())
            except:
                st.error("❌ Impossibile leggere il file Excel.")

        elif ext == "txt":
            with open(tmp_path, "r", encoding="utf-8") as f:
                text = f.read()
                st.text_area("📝 Contenuto TXT", text, height=200)

# -----------------------
# 💬 AI Chat Assistant
# -----------------------
if pdf_texts:
    st.header("🤖 Luna AI – Chiedi qualcosa sul report")
    full_text = "\n".join(pdf_texts)

    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "Sei una AI che analizza i contenuti PDF caricati e risponde con dati e analisi."},
            {"role": "user", "content": f"Contenuto PDF:\n\n{full_text}\n\nRispondi solo in base a questi contenuti."}
        ]

    domanda = st.text_input("✍️ Scrivi una domanda sul report")

    if domanda:
        st.session_state.messages.append({"role": "user", "content": domanda})
        with st.spinner("💭 Luna sta pensando..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message["content"]
            st.session_state.messages.append({"role": "assistant", "content": reply})

    for msg in st.session_state.messages[2:]:
        role = "🧑‍💻 Tu" if msg["role"] == "user" else "🤖 Luna"
        st.markdown(f"**{role}:** {msg['content']}")

    if st.session_state.messages[-1]["role"] == "assistant":
        response_txt = st.session_state.messages[-1]["content"]
        st.download_button("📥 Scarica risposta AI", response_txt, file_name="risposta_ai.txt", mime="text/plain")

# -----------------------
# ✉️ Email Sender
# -----------------------
st.header("📬 Invia Email con gli Allegati")
email_to = st.text_input("Destinatario email")
email_body = st.text_area("Messaggio", "In allegato trovi il report.")

if st.button("📤 Invia Email") and allegati and email_to:
    try:
        msg = MIMEMultipart()
        msg["From"] = "romanello.matteo87@gmail.com"
        msg["To"] = email_to
        msg["Subject"] = "📊 Report AI – da Luna"
        msg.attach(MIMEText(email_body, "plain"))

        for path in allegati:
            with open(path, "rb") as f:
                part = MIMEApplication(f.read(), _subtype="octet-stream")
                part.add_header("Content-Disposition", "attachment", filename=os.path.basename(path))
                msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login("romanello.matteo87@gmail.com", st.secrets["email_password"])
            server.send_message(msg)

        st.success("✅ Email inviata con successo!")

    except Exception as e:
        st.error(f"❌ Errore durante l'invio: {e}")
