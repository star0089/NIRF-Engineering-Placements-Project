# 03_scripts/download_govt_datasets.py

import os
import requests

def download_file(url, output_path):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Downloaded successfully: {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")

def main():
    os.makedirs("01_raw_data", exist_ok=True)

    datasets = {
        "AISHE":"https://cdnbbsr.s3waas.gov.in/s392049debbe566ca5782a3045cf300a3c/uploads/2024/02/20240719952688509.pdf",  
        "UGC University List": "https://www.ugc.gov.in/oldpdf/consolidated%20list%20of%20all%20universities.pdf",
        "NSDC Rajasthan Skill Gap": "https://nsdcindia.org/sites/default/files/files/NSDC%20Annual%20Report_updated_3_Dec_2024.pdf",
    }

    for name, url in datasets.items():
        filename = name.replace(" ", "_").lower() + ".pdf"
        output_path = os.path.join("01_raw_data", filename)
        print(f"\n📥 Downloading: {name}")
        download_file(url, output_path)

if __name__ == "__main__":
    main()
