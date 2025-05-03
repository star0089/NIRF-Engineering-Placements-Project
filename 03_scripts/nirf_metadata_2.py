import os
import re
import pdfplumber
import pandas as pd
from collections import defaultdict
import logging
from difflib import get_close_matches

# Setup logging for better debugging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()

def find_block_start(text: str, program_type: str) -> int:
    pattern = {
        "UG": r"(UG|Undergraduate)\s*(\[.*?\])?:\s*(Placement|Career)\s*&\s*(higher\s*studies|Higher\s*Studies)",
        "PG": r"(PG|Postgraduate)\s*(\[.*?\])?:\s*(Placement|Career)\s*&\s*(higher\s*studies|Higher\s*Studies)"
    }
    match = re.search(pattern[program_type], text, re.IGNORECASE)
    return match.start() if match else -1

def extract_placement_data(text, program_type):
    start = find_block_start(text, program_type)
    if start == -1:
        return []

    block = text[start:start + 8000].replace("\n", " ")

    pattern = re.compile(
        r"(\d{4}-\d{2})\s+(\d+)\s+(\d+)\s+([\d,]+)\([^)]*\)\s+(\d+)"
    )

    matches = pattern.findall(block)
    results = []
    seen = set()

    for match in matches:
        try:
            year, graduates, placed, salary_str, higher = match
            key = (program_type, year)
            if key in seen:
                continue
            seen.add(key)

            graduates = int(graduates)
            placed = int(placed)
            higher = int(higher)
            salary = float(salary_str.replace(",", "")) / 1e5

            if higher > graduates or higher > 500:
                continue
            if not year.startswith("20"):
                continue

            placement_pct = round((placed / graduates) * 100, 2) if graduates else 0

            results.append({
                "Program": program_type,
                "Year": year,
                "Graduates": graduates,
                "Placed": placed,
                "Median Salary (LPA)": round(salary, 2),
                "Higher Studies": higher,
                "Placement %": placement_pct
            })
        except Exception as e:
            print(f"⚠️ Error parsing record {match}: {e}")

    if not results:
        print(f"❌ No data matched for {program_type}.")
        print("🔍 Sample block:\n", block[:1000])

    return results

def extract_student_counts(pdf):
    male = female = total = 0

    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if not table:
                continue

            headers = [str(cell).replace("\n", " ") if cell else "" for cell in table[0]]
            if ("No. of Male Students" in headers and
                "No. of Female Students" in headers and
                "Total Students" in headers):

                for row in table[1:]:
                    if row[0] and row[0].startswith("UG"):
                        try:
                            m = int(row[1].replace(",", ""))
                            f = int(row[2].replace(",", ""))
                            t = int(row[3].replace(",", ""))
                            male += m
                            female += f
                            total += t
                        except:
                            continue
                if male > 0 and female > 0 and total > 0:
                    return male, female, total

    return None, None, None

# === MAIN SCRIPT ===
pdf_folder = r"D:\\Projects\\Not_completed\\Educational_Employment_Data_Project\\nirf_pdfs"
output_by_sheet = defaultdict(list)

# Loop over each file in the PDF folder
for file_name in sorted(os.listdir(pdf_folder)):
    if file_name.endswith(".pdf"):
        file_path = os.path.join(pdf_folder, file_name)
        with pdfplumber.open(file_path) as pdf:
            full_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])

            name_match = re.search(r"Institute Name:\s*(.+)", full_text)
            college_name = name_match.group(1).strip() if name_match else "Unknown"

            male, female, total = extract_student_counts(pdf)

            for prog in ["UG", "PG"]:
                if find_block_start(full_text, prog) == -1:
                    continue

                records = extract_placement_data(full_text, prog)
                for rec in records:
                    sheet_name = f"{prog}_{rec['Year']}"
                    rec.update({
                        "College Name": college_name,
                        "No. of Male Students": male,
                        "No. of Female Students": female,
                        "Total Students": total,
                        "File": file_name
                    })
                    output_by_sheet[sheet_name].append(rec)

if output_by_sheet:
    output_path = os.path.join(pdf_folder, "NIRF_Placements_Split_Yearwise.xlsx")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet, data in output_by_sheet.items():
            df = pd.DataFrame(data)
            df.drop_duplicates(inplace=True)
            df.to_excel(writer, index=False, sheet_name=sheet[:31])
    logger.info(f"✅ Data saved to: {output_path}")
else:
    logger.warning("No data to write to Excel.")