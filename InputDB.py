import pandas as pd
import mysql.connector
import numpy as np

# ===========================================
# 1. BACA CSV & SET HEADER MANUAL
# ===========================================
df = pd.read_csv("tkpi_clean.csv", header=None, dtype=str)

# DEBUG: Cek jumlah kolom di CSV
print(f"Jumlah kolom di CSV: {len(df.columns)}")
print(f"Kolom-kolom: {df.columns.tolist()}")

# Kolom yang diharapkan
expected_cols = [
    "kode","nama_bahan","sumber",
    "air","energi","protein","lemak","kh","serat","abu",
    "kalsium","fosfor","besi",
    "natrium","kalium",
    "tembaga","seng","retinol","bkar","kar_total",
    "tiamin","riboflavin","niasin","vit_c",
    "bdd"
]

# Jika jumlah kolom tidak sesuai, potong atau tambahkan
if len(df.columns) > len(expected_cols):
    print(f"WARNING: CSV punya {len(df.columns)} kolom, dipotong jadi {len(expected_cols)}")
    df = df.iloc[:, :len(expected_cols)]
elif len(df.columns) < len(expected_cols):
    print(f"ERROR: CSV cuma punya {len(df.columns)} kolom, butuh {len(expected_cols)}")
    exit()

df.columns = expected_cols
print(f"Kolom setelah rename: {df.columns.tolist()}\n")

# ===========================================
# 2. BERSIHKAN DATA DASAR
# ===========================================
df = df.replace({
    "?": None,
    "-": None,
    "": None,
    " ": None,
    "nan": None,  # Tambahan untuk string "nan"
    "NaN": None,
    "null": None,
    "NULL": None
})

# ===========================================
# 3. FIX ANGKA NGE-BUG (seperti "0.12 1.0")
# ===========================================
def fix_number(v):
    if v is None or pd.isna(v):
        return None
    
    v = str(v).strip().lower()
    
    # Cek jika string "nan" atau kosong
    if v in ["", "nan", "none", "null"]:
        return None
    
    # Jika ada dua angka → ambil angka pertama
    parts = v.split()
    if len(parts) > 1:
        v = parts[0]
    
    # Coba convert ke float
    try:
        result = float(v)
        # Jika hasilnya NaN, return None
        if np.isnan(result):
            return None
        return result
    except:
        return None

numeric_cols = [
    "air","energi","protein","lemak","kh","serat","abu",
    "kalsium","fosfor","besi",
    "natrium","kalium",
    "tembaga","seng","retinol","bkar","kar_total",
    "tiamin","riboflavin","niasin","vit_c",
    "bdd"
]

for col in numeric_cols:
    df[col] = df[col].apply(fix_number)

# ===========================================
# 4. PENTING: UBAH NaN → None AGAR SQL AMAN
# ===========================================
df = df.replace({np.nan: None, "nan": None, "NaN": None})
df = df.where(pd.notnull(df), None)

# ===========================================
# 5. KONEKSI KE DATABASE LARAVEL
# ===========================================
db = mysql.connector.connect(
    host="localhost",
    user="root",        # Ubah sesuai .env
    password="",        # Ubah sesuai .env
    database="laravel"  # Ubah jika DB beda
)

cursor = db.cursor()

# ===========================================
# 6. QUERY INSERT
# ===========================================
sql = """
INSERT INTO tkpi (
    kode, nama_bahan, sumber,
    air, energi, protein, lemak, kh, serat, abu,
    kalsium, fosfor, besi,
    natrium, kalium,
    tembaga, seng, retinol, bkar, kar_total,
    tiamin, riboflavin, niasin, vit_c,
    bdd,
    created_at, updated_at
) VALUES (
    %(kode)s, %(nama_bahan)s, %(sumber)s,
    %(air)s, %(energi)s, %(protein)s, %(lemak)s, %(kh)s, %(serat)s, %(abu)s,
    %(kalsium)s, %(fosfor)s, %(besi)s,
    %(natrium)s, %(kalium)s,
    %(tembaga)s, %(seng)s, %(retinol)s, %(bkar)s, %(kar_total)s,
    %(tiamin)s, %(riboflavin)s, %(niasin)s, %(vit_c)s,
    %(bdd)s,
    NOW(), NOW()
)
"""

# ===========================================
# 7. EKSEKUSI INSERT SEMUA BARIS CSV
# ===========================================
total = 0
errors = 0

print(f"Mulai insert {len(df)} baris...\n")

for idx, row in df.iterrows():
    try:
        # Konversi ke dict
        row_dict = row.to_dict()
        
        # DEBUG: Print baris pertama untuk cek struktur
        if idx == 0:
            print("DEBUG - Baris pertama:")
            print(f"Keys: {list(row_dict.keys())}")
            print(f"Sample data: {dict(list(row_dict.items())[:5])}\n")
        
        # Pastikan hanya kolom yang ada di SQL
        filtered_dict = {k: v for k, v in row_dict.items() if k in expected_cols}
        
        # Double check: replace any remaining NaN with None
        for key in filtered_dict:
            if pd.isna(filtered_dict[key]) or str(filtered_dict[key]).lower() == "nan":
                filtered_dict[key] = None
        
        cursor.execute(sql, filtered_dict)
        total += 1
        
        # Progress setiap 100 baris
        if total % 100 == 0:
            db.commit()
            print(f"Progress: {total} baris berhasil...")
            
    except Exception as e:
        errors += 1
        print(f"\nError di baris {idx}:")
        print(f"  Message: {e}")
        print(f"  Keys: {list(row_dict.keys())}")
        
        # Print 3 kolom pertama untuk debug
        sample = {k: row_dict[k] for k in list(row_dict.keys())[:3]}
        print(f"  Sample: {sample}\n")
        
        # Stop jika error di 5 baris pertama (kemungkinan ada masalah struktur)
        if idx < 5:
            print("ERROR CRITICAL: Masalah di 5 baris pertama, stop eksekusi")
            db.close()
            exit()

# Commit sisanya
db.commit()
db.close()

print(f"\n{'='*50}")
print(f"SUKSES! {total} data berhasil dimasukkan")
if errors > 0:
    print(f"GAGAL: {errors} baris gagal dimasukkan")
print(f"{'='*50}")