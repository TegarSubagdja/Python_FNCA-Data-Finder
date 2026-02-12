import camelot
import pandas as pd
import re

# regex baris data (2 huruf + 3 angka)
pattern = re.compile(r"^[A-Za-z]{2}\d{3}")

# baca semua tabel di halaman 15-20
tables = camelot.read_pdf("data.pdf", pages="15-83")

filtered_rows = []

# proses setiap tabel
for t in tables:
    df = t.df

    for _, row in df.iterrows():
        first_cell = str(row[0]).strip()

        # hanya ambil baris yang cocok regex
        if pattern.match(first_cell):
            filtered_rows.append(row.tolist())

# convert ke DataFrame akhir
df_final = pd.DataFrame(filtered_rows)

# simpan ke satu sheet
df_final.to_excel("data.xlsx", sheet_name="Gabungan", index=False)

print("Berhasil! Hanya baris data (regex) yang disimpan ke satu sheet.")
