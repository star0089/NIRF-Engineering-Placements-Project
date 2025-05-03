# 📊 Educational Employment Data Analysis (NIRF-Based)

This project analyzes **engineering placements** data from NIRF PDFs of Indian institutes. The goal is to extract, clean, and analyze UG/PG placement trends across years using Python.

---

## 📁 Project Structure

```
.
├── 01_data/
│   ├── nirf_pdfs/                  # Raw NIRF PDF files
│   ├── NIRF_Placements_Split_Yearwise.xlsx
│   └── NIRF_Placements_Split_Yearwise_CLEANED.xlsx

├── 02_scripts/
│   ├── download_govt_datasets.py     # Download PDFs (if applicable)
│   ├── Pdf_data_extraction.py        # Basic PDF parsing
│   ├── nirf_metadata_2.py            # Main placement extraction logic
│   ├── placement_excel_polisher.py   # Excel cleaning
│   ├── prepare_final_dataset.py      # Combine/filter datasets
│   ├── Get_collage table.py          # Supporting metadata extraction
│   └── Cleaner.py                    # Additional clean-up helpers

├── 03_scripts/
│   ├── EDA-Notebook.py               # Final visualization/EDA
│
├── README.md
├── requirements.txt
```

---

## 🧠 Features

- 🔍 Extracts UG and PG placement data from raw NIRF PDFs.
- 📊 Cleans and merges multi-year, multi-college data into a structured Excel.
- 📈 Visualizes trends like:
  - Average Median Salary by Program
  - Year-wise Salary Trends
  - Placement Percentages
  - Correlation Heatmaps
  - Top Performing Colleges

---

## 🚀 How to Run

1. **Step 1** – Place raw NIRF PDF files inside `nirf_pdfs/`.
2. **Step 2** – Extract and convert PDFs:
   ```bash
   python nirf_metadata_2.py
   ```

3. **Step 3** – Clean the Excel:
   ```bash
   python placement_excel_polisher.py
   ```

4. **Step 4** – Run final analysis and EDA:
   ```bash
   python EDA-Notebook.py
   ```

---

## 🧪 Sample Outputs

- `NIRF_Placements_Split_Yearwise.xlsx` – Raw extracted data
- `NIRF_Placements_Split_Yearwise_CLEANED.xlsx` – Cleaned for EDA

---

## 🛠 Requirements

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🧹 Cleaning Rules

- Dropped rows with 0 graduates/placed/higher unless it's recent data (2021, 2022)
- Removed placement percentage > 100%
- Normalized string and numeric formats

---

## 📊 Visualization Insights

EDA script includes:

- Bar plots, line charts for trends
- Box plots for placement distribution
- Correlation matrix between salary, placements, higher studies

---

## ⚠️ Known Issues

- ❗ **Data Availability Gaps**: Not all colleges have data available for all years. This leads to inconsistencies in trend lines and box plots.
- 📉 Missing years can skew average salary or placement % trends.
- 📥 PDF table extraction sometimes skips rows due to poor formatting or scanned documents.

---

## 👨‍💻 Author

Project by Mahesh Vyas – Built using `pandas`, `pdfplumber`, `seaborn`, `matplotlib`, and `openpyxl`.