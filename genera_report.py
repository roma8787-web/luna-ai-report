from fpdf import FPDF

# 📄 Istanza PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=14)

# 📋 Contenuto del report
pdf.cell(200, 10, txt="Report Settimanale - Esempio", ln=True, align="C")
pdf.ln(10)
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, txt="""
Questo è un report di esempio generato automaticamente.

Numero clienti: 58
Ordini effettuati: 124
Fatturato totale: 3580.50 EUR

Generato automaticamente da Python.
""")

# 💾 Salva il PDF
pdf.output("report.pdf")
print("✅ Report PDF generato con successo.")