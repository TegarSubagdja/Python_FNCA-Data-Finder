import fitz  # PyMuPDF
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route("/search")
def search():
    query = request.args.get("q")
    pdf_path = "data.pdf"

    if not query:
        return "Parameter q diperlukan", 400

    doc = fitz.open(pdf_path)

    for page_number, page in enumerate(doc):

        # 1. Cari teks + posisi bounding box dengan PyMuPDF
        text_instances = page.search_for(query)

        if text_instances:
            # 2. Tambahkan highlight annotation (efek stabilo)
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.update()

            # 3. Render halaman dengan highlight
            pix = page.get_pixmap(dpi=150)
            image_path = f"highlight_page_{page_number+1}.png"
            pix.save(image_path)

            return send_file(image_path, mimetype="image/png")

    return "Teks tidak ditemukan", 404


if __name__ == "__main__":
    app.run(debug=True)
