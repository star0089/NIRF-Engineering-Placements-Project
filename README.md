# NIRF Engineering Placement Analysis

Python extraction and exploration of institutional placement disclosures, with Excel datasets and a Power BI dashboard.

## Purpose

Compare reported graduates, placements, higher-study counts and median salaries across available institution/program/year records. This supports exploration of education outcomes; it does not establish why institutions perform differently or represent all Indian engineering colleges.

**Status:** Extraction scripts, workbooks, EDA code and dashboard artifacts are committed. The EDA entry point is portable; the broader extraction pipeline still needs path configuration and source-level validation.

## Existing outputs

![Existing placement dashboard](05_Visualization/Nirf%20PLacement%20Dashboard.png)

- [Power BI dashboard](05_Visualization/Placement_Gap.py.pbix)
- [Extracted placement workbook](nirf_pdfs/NIRF_Placements_Split_Yearwise.xlsx)
- [Cleaned placement workbook](nirf_pdfs/NIRF_Placements_Split_Yearwise_CLEANED.xlsx)

The extracted workbook contains six UG/PG year sheets covering 2020–21, 2021–22 and 2022–23, with 112 rows across sheets. This is extracted coverage, not a claim of complete coverage. Numerical findings require reconciliation against the source PDFs.

## Repository navigation

| Location | Contents |
| --- | --- |
| `nirf_pdfs/` | 84 numbered source PDFs and placement workbooks |
| `01_raw_data/` | Supporting government PDFs and category workbooks |
| `03_scripts/` | Extraction, cleaning and dataset-preparation scripts |
| `03_cleaned_data/` | Existing prepared datasets |
| `04_eda_notebooks/EDA-Notebook.py` | Python plotting script, despite the folder name |
| `04_reports/` | Existing cleaning reports |
| `05_Visualization/` | Dashboard PNG and PBIX |
| [docs/methodology.md](docs/methodology.md) | Definitions, execution boundaries and validation priorities |

## Run the existing EDA

From the repository root, create a Python environment and install the committed dependencies:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python 04_eda_notebooks/EDA-Notebook.py --output outputs/ug-placement-eda.png
```

Use your environment's Python after activating it. To select another worksheet:

```bash
python 04_eda_notebooks/EDA-Notebook.py --sheet UG_2022-23 --output outputs/ug-2022-23.png
```

The default remains the **first worksheet only**, preserving original analytical behavior. It does not combine all years. Use `--input PATH` for another compatible workbook. Without `--output`, a chart window opens.

Dependencies are pinned in [requirements.txt](requirements.txt). A supported Python-version range and a clean-environment install have not yet been established.

## Methodology and limitations

The cleaner strips text, attempts numeric conversion, removes all-null key rows, excludes placement percentages above 100 and conditionally removes all-zero records. The recent-year exception is hard-coded to 2021/2022; it is not a general recency policy.

Charts average institutional median salaries; that is **not** a pooled graduate salary median. Missing institution-years and extraction failures can bias comparisons. Salary units and placement denominators must be checked against source disclosures.

Other extraction scripts still contain local Windows paths, and OCR/browser utilities need dependencies beyond the EDA requirements. The previous README's end-to-end commands were therefore removed. No extraction or cleaning definitions have been changed in this pass.

## Next improvements

1. Validate sampled workbook rows and units against source PDFs.
2. Configure extraction/cleaning paths and record source provenance.
3. Document missingness and coverage by institution/year.
4. Design an explicit all-sheet analysis before making multi-year claims.

**Mahesh Vyas** · [LinkedIn](https://www.linkedin.com/in/data-mahesh/) · [GitHub](https://github.com/star0089)
