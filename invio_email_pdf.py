import streamlit as st
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os

st.set_page_config(page_title="📧 Invia Report Email", layout="centered")
st.title("📧 Invia un Report PDF via Email")

# 📥 Inserisci destinatario
destinatario = st.text_input("✉️ Inserisci l'email del destinatario")

# 📂 Carica un file PDF
file_caricato = st.file_uploader("📎 Carica un file PDF", type=["pdf"])

# 📬 Mittente (già configurato)
mittente = "romanello.matteo87@gmail.com"
password = "xljklbmsrltazkny"

# 📨 Invia email
if st.button("📤 Invia Email"):
    if not destinatario or not file_caricato:
        st.warning("⚠️ Inserisci un destinatario e carica un file.")
    else:
        try:
            msg = MIMEMultipart()
            msg["From"] = mittente
            msg["To"] = destinatario
            msg["Subject"] = "📊 Report Allegato"
            msg.attach(MIMEText("Ciao! In allegato trovi il report richiesto.", "plain"))

            # Leggi il file caricato
            parte_pdf = MIMEApplication(file_caricato.read(), _subtype="pdf")
            parte_pdf.add_header("Content-Disposition", "attachment", filename=file_caricato.name)
            msg.attach(parte_pdf)

            # Invia email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(mittente, password)
                server.send_message(msg)

            st.success("✅ Email inviata con successo!")

        except Exception as e:
            st.error(f"❌ Errore durante l'invio: {e}")