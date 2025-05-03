import re
import pandas as pd
import pdfplumber

# Define function to extract student strength data
def extract_student_strength(text):
    # Pattern for UG and PG data
    pattern = r"UG \[.*?\]\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
    pg_pattern = r"PG \[.*?\]\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"

    match = re.search(pattern, text)
    pg_match = re.search(pg_pattern, text)

    data = []

    # Extract UG Data
    if match:
        values = list(map(int, match.groups()))
        data.append({
            "Program": "UG",
            "Male": values[0],
            "Female": values[1],
            "Total": values[2],
            "Within State": values[3],
            "Outside State": values[4],
            "Foreign": values[5],
            "EWS": values[6],
            "SC/ST/OBC": values[7],
            "Free Fee (State)": values[8],
            "Free Fee (Institution)": values[9],
            "Free Fee (Private)": values[10],
            "No Free Fee": values[11]
        })

    # Extract PG Data
    if pg_match:
        values = list(map(int, pg_match.groups()))
        data.append({
            "Program": "PG",
            "Male": values[0],
            "Female": values[1],
            "Total": values[2],
            "Within State": values[3],
            "Outside State": values[4],
            "Foreign": values[5],
            "EWS": values[6],
            "SC/ST/OBC": values[7],
            "Free Fee (State)": values[8],
            "Free Fee (Institution)": values[9],
            "Free Fee (Private)": values[10],
            "No Free Fee": values[11]
        })

    return data

# Define function to extract year-wise intake data
def extract_year_wise_intake(text):
    year_pattern = r"(\d{4})\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
    matches = re.findall(year_pattern, text)
    
    year_data = []
    for match in matches:
        year_data.append({
            "Year": match[0],
            "UG Intake": match[1],
            "PG Intake": match[2],
            "Total Intake": match[3],
            "Actual UG Enrolled": match[4],
            "Actual PG Enrolled": match[5]
        })
    
    return year_data

# Define function to extract placement data
def extract_placement_data(text):
    placement_pattern = r"(\d{4})\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d\.]+)"
    matches = re.findall(placement_pattern, text)
    
    placement_data = []
    for match in matches:
        placement_data.append({
            "Year": match[0],
            "No. of Graduates": match[1],
            "No. Placed": match[2],
            "Median Salary (₹)": match[3],
            "Median Salary (LPA)": match[4]
        })

    return placement_data

# Define function to extract PhD data (if required)
def extract_phd_data(text):
    phd_pattern = r"Total PhD Students\s+(\d+)\s+(\d+)\s+(\d+)"
    phd_match = re.search(phd_pattern, text)

    phd_data = []
    if phd_match:
        phd_data.append({
            "Full-time PhD Students": phd_match.group(1),
            "Part-time PhD Students": phd_match.group(2),
            "PhD Graduates per Year": phd_match.group(3)
        })

    return phd_data

# Define function to extract financial data (optional)
def extract_financial_data(text):
    financial_pattern = r"Capital Expenditure\s+(\d+)\s+(\d+)\s+(\d+)"
    financial_match = re.search(financial_pattern, text)

    financial_data = []
    if financial_match:
        financial_data.append({
            "Library": financial_match.group(1),
            "Equipment": financial_match.group(2),
            "Workshops": financial_match.group(3)
        })
    
    return financial_data

# Define function to extract research and consultancy data (optional)
def extract_research_data(text):
    research_pattern = r"Sponsored Projects\s+(\d+)\s+(\d+)\s+(\d+)"
    consultancy_pattern = r"Consultancy Projects\s+(\d+)\s+(\d+)\s+(\d+)"

    research_matches = re.findall(research_pattern, text)
    consultancy_matches = re.findall(consultancy_pattern, text)

    research_data = []
    consultancy_data = []

    for match in research_matches:
        research_data.append({
            "Sponsored Projects": match[0],
            "Funding": match[1],
            "Total Projects": match[2]
        })

    for match in consultancy_matches:
        consultancy_data.append({
            "Consultancy Projects": match[0],
            "Consulting Fee": match[1],
            "Total Projects": match[2]
        })

    return research_data, consultancy_data

# Function to extract all data from PDF
def extract_all_data_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text()

    demographics = extract_student_strength(full_text)
    year_wise_intake = extract_year_wise_intake(full_text)
    placement_data = extract_placement_data(full_text)
    phd_data = extract_phd_data(full_text)
    financial_data = extract_financial_data(full_text)
    research_data, consultancy_data = extract_research_data(full_text)

    return demographics, year_wise_intake, placement_data, phd_data, financial_data, research_data, consultancy_data

# Save the extracted data to Excel
def save_to_excel(demographics, year_wise_intake, placement_data, phd_data, financial_data, research_data, consultancy_data):
    with pd.ExcelWriter("NIRF_Advanced_Data.xlsx") as writer:
        pd.DataFrame(demographics).to_excel(writer, sheet_name="Student_Demographics", index=False)
        pd.DataFrame(year_wise_intake).to_excel(writer, sheet_name="Year_Wise_Intake", index=False)
        pd.DataFrame(placement_data).to_excel(writer, sheet_name="Placement_Data", index=False)
        pd.DataFrame(phd_data).to_excel(writer, sheet_name="PhD_Data", index=False)
        pd.DataFrame(financial_data).to_excel(writer, sheet_name="Financial_Data", index=False)
        pd.DataFrame(research_data).to_excel(writer, sheet_name="Research_Data", index=False)
        pd.DataFrame(consultancy_data).to_excel(writer, sheet_name="Consultancy_Data", index=False)

    print("Data has been successfully extracted and saved to NIRF_Advanced_Data.xlsx")

# Main function to run the entire process
def main(pdf_file):
    demographics, year_wise_intake, placement_data, phd_data, financial_data, research_data, consultancy_data = extract_all_data_from_pdf(pdf_file)
    save_to_excel(demographics, year_wise_intake, placement_data, phd_data, financial_data, research_data, consultancy_data)

# Run the main function
main("NIRF_Report.pdf")
