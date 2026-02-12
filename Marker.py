import fitz  # PyMuPDF

pdf_path = "data.pdf"
text_to_find = "Beras giling var pelita, mentah"

doc = fitz.open(pdf_path)

for page in doc:
    results = page.search_for(text_to_find)

    for rect in results:
        # highlight langsung di PDF
        highlight = page.add_highlight_annot(rect)
        highlight.update()

doc.save("hasil_marked.pdf")
doc.close()

print("Selesai! File tersimpan sebagai hasil_marked.pdf")
