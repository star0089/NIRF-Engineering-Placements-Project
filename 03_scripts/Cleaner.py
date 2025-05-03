import os
import pdfplumber
import pandas as pd
import re
from collections import defaultdict
import logging
from difflib import get_close_matches

# Setup logging for better debugging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger()

# Load NIRF_MAIN.xlsx to get rank, score, and state
nirf_main_path = r"D:\\Projects\\Not_completed\\Educational_Employment_Data_Project\\nirf_pdfs\\NIRF_MAIN.xlsx"
nirf_df = pd.read_excel(nirf_main_path, sheet_name='Enginearing')
nirf_df['name_clean'] = nirf_df['name'].str.replace("More Details.*", "", regex=True).str.strip().str.lower()

def get_nirf_metadata(college_name):
    match = get_close_matches(college_name.lower(), nirf_df['name_clean'], n=1, cutoff=0.7)
    if match:
        row = nirf_df[nirf_df['name_clean'] == match[0]].iloc[0]
        return int(row['rank']), row['score'], row['state']
    return "NA", "NA", "NA"

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

    results = []
    seen_years = set()

    for match in pattern.findall(block):
        try:
            year, graduates, placed, salary_str, higher = match
            if year in seen_years:
                continue  # Skip duplicate years
            seen_years.add(year)

            graduates = int(graduates)
            placed = int(placed)
            higher = int(higher)
            salary = float(salary_str.replace(",", "")) / 1e5  # Convert to LPA
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

    return results

def extract_student_counts(text):
    pattern = re.compile(r"No\\. of Male\\s*Students\\s*(\\d+)[^\\d]+No\\. of Female\\s*Students\\s*(\\d+)[^\\d]+Total Students[^\\d]+(\\d+)", re.DOTALL)
    match = pattern.search(text)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
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

            # Extract college info
            name_match = re.search(r"Institute Name:\s*(.+)", full_text)
            college_name = name_match.group(1).strip() if name_match else "Unknown"

            rank, score, state = get_nirf_metadata(college_name)
            male, female, total = extract_student_counts(full_text)

            # Extract data for both UG and PG placements, regardless of whether they exist
            for prog in ["UG", "PG"]:
                records = extract_placement_data(full_text, prog)
                for rec in records:
                    sheet_name = f"{prog}_{rec['Year']}"
                    rec.update({
                        "College Name": college_name,
                        "NIRF Rank": rank,
                        "NIRF Score": score,
                        "State": state,
                        "No. of Male Students": male,
                        "No. of Female Students": female,
                        "Total Students": total,
                        "File": file_name
                    })
                    output_by_sheet[sheet_name].append(rec)

# Check if there is any data to write to Excel
if output_by_sheet:
    output_path = os.path.join(pdf_folder, "NIRF_Placements_Split_Yearwise.xlsx")
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet, data in output_by_sheet.items():
            df = pd.DataFrame(data)
            df.drop_duplicates(inplace=True)  # Final deduplication before saving
            df.to_excel(writer, index=False, sheet_name=sheet[:31])  # Excel sheet name limit
    logger.info(f"✅ Data saved to: {output_path}")
else:
    logger.warning("No data to write to Excel.")
