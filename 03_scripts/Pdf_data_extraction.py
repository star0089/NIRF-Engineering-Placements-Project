import os
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
import pandas as pd
from PIL import Image, ImageFilter, ImageEnhance

# CONFIGURATION
PDF_PATH = r"D:\Projects\Not_completed\Educational_Employment_Data_Project\01_raw_data\pdf\aishe.pdf"
OUTPUT_FOLDER = r"d:\Projects\Not_completed\Educational_Employment_Data_Project\02_processed_data"
POPPLER_PATH = r"C:\poppler\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def is_scanned_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                print(f"\n🔍 Sample text from page: {text[:100] if text else 'No text found'}")
                if text:
                    return False
        return True
    except Exception as e:
        print(f"   ❌ Error in scanned check: {e}")
        return True

def extract_from_digital(pdf_path):
    dfs = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"\n📄 Page {i+1} digital extraction")
            tables = page.extract_tables()
            print(f"   📊 Tables found: {len(tables)}")
            for t in tables:
                for row in t:
                    print(f"   🧾 Row: {row}")
                df = pd.DataFrame(t[1:], columns=t[0])
                dfs.append(df)
    return dfs

def preprocess_image(image):
    image = image.convert("L")
    image = image.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    return image

def extract_from_scanned(pdf_path):
    dfs = []
    images = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    for idx, img in enumerate(images):
        print(f"\n🖼️ Processing scanned page {idx+1}")
        img = preprocess_image(img)
        text = pytesseract.image_to_string(img, config='--psm 6')
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        print(f"   🧾 OCR lines: {lines[:5]}")
        rows = [line.split() for line in lines if len(line.split()) > 1]
        for row in rows:
            print(f"   📌 Row: {row}")
        if rows:
            df = pd.DataFrame(rows)
            dfs.append(df)
    return dfs

def save_to_excel(dfs, filename):
    out_file = os.path.join(OUTPUT_FOLDER, os.path.splitext(os.path.basename(filename))[0] + "_DEBUG.xlsx")
    with pd.ExcelWriter(out_file, engine='openpyxl') as writer:
        for i, df in enumerate(dfs):
            df.to_excel(writer, sheet_name=f"Sheet_{i+1}", index=False)
    print(f"\n✅ Excel saved to: {out_file}")

def main():
    print(f"\n📁 Testing file: {PDF_PATH}")
    scanned = is_scanned_pdf(PDF_PATH)
    print(f"🔎 Detected as: {'Scanned (OCR)' if scanned else 'Digital'}")

    dfs = extract_from_scanned(PDF_PATH) if scanned else extract_from_digital(PDF_PATH)
    if not dfs:
        print("\n❌ No data extracted.")
    else:
        save_to_excel(dfs, PDF_PATH)

if __name__ == "__main__":
    main()
