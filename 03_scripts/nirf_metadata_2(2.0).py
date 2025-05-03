import os
import pdfplumber
import pandas as pd
import re
from collections import defaultdict
import logging
import requests
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get NIRF rank from the website
def get_nirf_ranks():
    url = 'https://www.nirfindia.org/Rankings/2024/EngineeringRanking.html'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    college_ranks = {}
    table = soup.find('table', {'class': 'table'})
    rows = table.find_all('tr')[1:]  # Skip header

    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 2:
            rank = cols[0].get_text(strip=True)
            college_name = cols[1].get_text(strip=True)
            college_ranks[college_name] = rank

    return college_ranks

# Function to find block start (UG/PG)
def find_block_start(text, program_type):
    patterns = {
        "UG": r"UG \[.*?\]\s*:\s*Placement\s*&\s*Higher\s*Studies",
        "PG": r"PG \[.*?\]\s*:\s*Placement\s*&\s*Higher\s*Studies"
    }
    match = re.search(patterns[program_type], text, re.IGNORECASE)
    return match.start() if match else -1

# Function to extract placement data from IIT-style NIRF PDFs
def extract_placement_data(text, program_type):
    start = find_block_start(text, program_type)
    if start == -1:
        return []

    block = text[start:start + 6000].replace("\n", " ")

    # Match structure: academic years, graduated, placed, salary, higher
    pattern = re.compile(
        r"(20\d{2}-\d{2})\s+\d+\s+\d+\s+(20\d{2}-\d{2})\s+(\d+)\s+(\d+)\s+([\d,]+)\([^)]*\)\s+(\d+)"
    )

    results = []

    for match in pattern.findall(block):
        try:
            _, year, graduates, placed, salary_str, higher = match
            graduates = int(graduates)
            placed = int(placed)
            higher = int(higher)
            salary_lpa = round(int(re.sub(r"[^\d]", "", salary_str)) / 1e5, 2)
            placement_pct = round((placed / graduates) * 100, 2) if graduates else 0

            results.append({
                "Program": program_type,
                "Year": year,
                "Graduates": graduates,
                "Placed": placed,
                "Median Salary (LPA)": salary_lpa,
                "Higher Studies": higher,
                "Placement %": placement_pct
            })
        except Exception as e:
            logger.warning(f"Error parsing placement row: {match} — {e}")

    return results

# Main script to process all PDFs in a folder
def process_nirf_pdfs(pdf_folder):
    output_by_sheet = defaultdict(list)
    nirf_ranks = get_nirf_ranks()

    for file_name in sorted(os.listdir(pdf_folder)):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(pdf_folder, file_name)
            try:
                with pdfplumber.open(file_path) as pdf:
                    full_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])

                    name_match = re.search(r"Institute Name:\s*(.+?)\s*(\[|\n)", full_text)
                    college_name = name_match.group(1).strip() if name_match else "Unknown"
                    rank = nirf_ranks.get(college_name, "NA")

                    for prog in ["UG", "PG"]:
                        records = extract_placement_data(full_text, prog)
                        if not records:
                            logger.info(f"No {prog} placement data found for: {college_name}")
                            continue

                        for rec in records:
                            sheet_name = f"{prog}_{rec['Year']}"
                            rec.update({
                                "College Name": college_name,
                                "NIRF Rank": rank,
                                "File": file_name
                            })
                            output_by_sheet[sheet_name].append(rec)
            except Exception as e:
                logger.warning(f"Error processing file {file_name}: {e}")

    if output_by_sheet:
        output_path = os.path.join(pdf_folder, "NIRF_Placements_Split_Yearwise.xlsx")
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet, data in output_by_sheet.items():
                df = pd.DataFrame(data)
                df.to_excel(writer, index=False, sheet_name=sheet[:31])
        logger.info(f"✅ Data saved to: {output_path}")
    else:
        logger.warning("⚠️ No data to write to Excel.")

# Run script if executed directly
if __name__ == "__main__":
    pdf_folder = r"D:\\Projects\\Not_completed\\Educational_Employment_Data_Project\\nirf_pdfs"
    process_nirf_pdfs(pdf_folder)