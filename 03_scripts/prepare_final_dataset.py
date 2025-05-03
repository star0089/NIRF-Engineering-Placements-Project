# 📚 Import Libraries
import pandas as pd
import numpy as np
import logging
from fuzzywuzzy import fuzz, process
import os

# 📄 Set up Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 📂 File Paths
nirf_file = r"D:\Projects\Not_completed\Educational_Employment_Data_Project\03_cleaned_data\NIRF_MAIN.xlsx"
aishe_file = r"D:\Projects\Not_completed\Educational_Employment_Data_Project\03_cleaned_data\cleaned_AISHE.xlsx"
ugc_file = r"D:\Projects\Not_completed\Educational_Employment_Data_Project\03_cleaned_data\cleaned_UGC University List.xlsx"
nsdc_file = r"D:\Projects\Not_completed\Educational_Employment_Data_Project\03_cleaned_data\cleaned_Skill Gap Rajasthan.xlsx"

# 🧹 Basic Column Cleaner
def basic_clean(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^\w\s]', '', regex=True)
    return df

# ✨ Clean Text for Matching
def clean_text(s):
    if pd.isna(s):
        return ""
    return ''.join(e for e in str(s).lower().strip() if e.isalnum() or e.isspace())

# 🔍 Normalize Columns
def normalize_college(df, new_col='college_name'):
    college_like_cols = [c for c in df.columns if any(x in c for x in ['name', 'college', 'institute', 'institution', 'university']) and 'id' not in c]
    if college_like_cols:
        df.rename(columns={college_like_cols[0]: new_col}, inplace=True)
        logging.info(f"🔑 Renamed '{college_like_cols[0]}' to '{new_col}'.")
    else:
        raise KeyError("No suitable college name column found.")
    return df

def normalize_state(df):
    state_like_cols = [c for c in df.columns if 'state' in c]
    if state_like_cols:
        df.rename(columns={state_like_cols[0]: 'state'}, inplace=True)
        logging.info(f"🔑 Renamed '{state_like_cols[0]}' to 'state'.")
    else:
        logging.warning("⚠️ No state-like column found. Filling with 'Unknown'.")
        df['state'] = 'Unknown'
    return df

def normalize_university(df):
    university_like_cols = [c for c in df.columns if any(x in c for x in ['university', 'college', 'institute', 'institution', 'name'])]
    if university_like_cols:
        df.rename(columns={university_like_cols[0]: 'university_name'}, inplace=True)
        logging.info(f"🔑 Renamed '{university_like_cols[0]}' to 'university_name'.")
    else:
        raise KeyError("No suitable university name column found.")
    return df

# 🔍 Fuzzy Merge
def fuzzy_merge(df1, df2, key1, key2, threshold=90):
    s = df2[key2].dropna().unique().tolist()
    matches = df1[key1].apply(lambda x: process.extractOne(str(x), s, scorer=fuzz.token_sort_ratio) if pd.notna(x) else (np.nan, 0))
    df1['best_match'] = matches.apply(lambda x: x[0] if x[1] >= threshold else np.nan)
    return df1

# 🛠 Main Function
def prepare_data():
    try:
        logging.info('📥 Loading datasets...')
        nirf = pd.read_excel(nirf_file)
        aishe = pd.read_excel(aishe_file)
        ugc = pd.read_excel(ugc_file)

        # Try loading NSDC, handle if missing
        if os.path.exists(nsdc_file):
            nsdc = pd.read_excel(nsdc_file)
            nsdc = basic_clean(nsdc)
            nsdc = normalize_state(nsdc)
            nsdc_loaded = True
        else:
            logging.warning(f"⚠️ NSDC file not found at {nsdc_file}. Skipping NSDC merge.")
            nsdc_loaded = False

        logging.info('🧹 Cleaning column names...')
        nirf = basic_clean(nirf)
        aishe = basic_clean(aishe)
        ugc = basic_clean(ugc)

        logging.info('🔑 Renaming key columns...')
        nirf = normalize_college(nirf)
        aishe = normalize_college(aishe)
        ugc = normalize_university(ugc)
        nirf = normalize_state(nirf)
        aishe = normalize_state(aishe)

        logging.info('🧼 Cleaning text fields...')
        nirf['college_name_clean'] = nirf['college_name'].apply(clean_text)
        aishe['college_name_clean'] = aishe['college_name'].apply(clean_text)

        logging.info('🔍 Fuzzy matching...')
        nirf = fuzzy_merge(nirf, aishe, 'college_name_clean', 'college_name_clean')

        total_nirf = len(nirf)
        matched_nirf = nirf['best_match'].notna().sum()
        unmatched_nirf = total_nirf - matched_nirf
        match_rate = matched_nirf / total_nirf * 100

        logging.info(f'📈 Total NIRF colleges: {total_nirf}')
        logging.info(f'✅ Successfully matched: {matched_nirf}')
        logging.info(f'❌ Unmatched: {unmatched_nirf}')
        logging.info(f'🎯 Match rate: {match_rate:.2f}%')

        nirf[nirf['best_match'].isna()].to_csv('unmatched_nirf_colleges.csv', index=False)

        matched_nirf_df = nirf.dropna(subset=['best_match'])
        if matched_nirf_df.empty:
            logging.error("❌ No matched colleges found. Stopping pipeline.")
            return

        logging.info('🔗 Merging matched datasets...')
        merged = pd.merge(matched_nirf_df, aishe, left_on='best_match', right_on='college_name_clean', how='left', suffixes=('_nirf', '_aishe'))

        logging.info('🏫 Merging with UGC...')
        merged = pd.merge(merged, ugc, left_on='college_name_nirf', right_on='university_name', how='left')

        if nsdc_loaded:
            logging.info('🛠️ Merging with NSDC skill gap data...')
            merged = pd.merge(merged, nsdc, left_on='state_nirf', right_on='state', how='left')

        logging.info('🧠 Optimizing memory usage...')
        for col in merged.select_dtypes(include=['float64']).columns:
            merged[col] = pd.to_numeric(merged[col], downcast='float')
        for col in merged.select_dtypes(include=['int64']).columns:
            merged[col] = pd.to_numeric(merged[col], downcast='integer')

        fill_dict = {'type': 'Unknown', 'status': 'Unknown'}
        if nsdc_loaded:
            fill_dict['projected_skill_gap'] = 0

        merged.fillna(fill_dict, inplace=True)

        output_file = 'final_education_skill_gap_advanced.csv'
        merged.to_csv(output_file, index=False)
        logging.info(f'✅ Final dataset saved as: {output_file}')

    except Exception as e:
        logging.error(f'❌ Error during data preparation: {e}')

# 🏁 Run
if __name__ == "__main__":
    prepare_data()
