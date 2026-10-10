# Methodology and reproducibility notes

## Observed data structure

The extracted placement workbook contains 112 rows across six sheets: UG_2020-21 (21), UG_2021-22 (13), PG_2021-22 (14), PG_2022-23 (22), UG_2022-23 (28), PG_2020-21 (14).

Columns include Program, Year, Graduates, Placed, Higher Studies, Placement %, Median Salary (LPA), College Name, student demographics and File. Intended grain is institution/program/year; uniqueness and source completeness have not yet been validated.

## EDA behavior

The plotting script reads one sheet, strips column whitespace, filters Program values containing UG, then plots means, a salary trend, a placement distribution and top institutions by mean median salary. Default sheet selection remains unchanged. Selecting a single-year sheet yields a single-year chart, not a longitudinal result.

The new CLI changes file configuration and figure saving only. Workbook values, groupings and cleaning rules remain unchanged.

## Known engineering gaps

- Multiple extraction/cleaning scripts contain hard-coded local paths.
- OCR code requires external Tesseract/Poppler configuration.
- Browser/OCR/downloader dependencies are not covered by the existing EDA requirements.
- Duplicate output locations, debug workbooks, an editor scratch script and a bundled browser driver remain in the baseline; they were not removed without establishing their role.
- Data redistribution permissions and source URL provenance need documentation.

## Validation performed

Inspected the tracked file inventory, EDA and cleaner code, path references, workbook sheet names/columns and row counts. Ran the portable EDA against the committed workbook with a noninteractive plotting backend and inspected its image. Checked the new relative README links.

Existing seaborn palette calls emit future deprecation warnings; charts currently render. No complete extraction, Power BI refresh or source-PDF accuracy validation was performed. No claims of nationwide coverage, causal effects or improved placement outcomes are made.
