"""
Kaggle Dataset Downloader for Smart Judicial Case Timeline Analyzer.
Downloads Indian legal judgment datasets using Kaggle API.

Usage:
    python setup_kaggle.py

Prerequisites:
    1. Install: pip install opendatasets kagglehub
    2. Kaggle API credentials:
       - Go to https://www.kaggle.com/settings → Create New Token
       - Place kaggle.json in ~/.kaggle/ (Linux/Mac) or C:\\Users\\<user>\\.kaggle\\ (Windows)
       OR
       - Set environment variables: KAGGLE_USERNAME and KAGGLE_KEY
"""

import os
import sys

# Set Kaggle API credentials
os.environ["KAGGLE_USERNAME"] = "pagadalamohith"
os.environ["KAGGLE_KEY"] = "KGAT_89e5bcbd87cffaf1ba6af1e18cabffd3"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def download_with_opendatasets():
    """Download datasets using opendatasets library."""
    try:
        import opendatasets as od
    except ImportError:
        print("Installing opendatasets...")
        os.system(f"{sys.executable} -m pip install opendatasets")
        import opendatasets as od

    os.makedirs(DATA_DIR, exist_ok=True)

    datasets = [
        {
            "url": "https://www.kaggle.com/datasets/vangmanern/indian-supreme-court-judgments",
            "name": "Indian Supreme Court Judgments",
            "description": "PDF/text judgments for OCR & NLP processing"
        },
        {
            "url": "https://www.kaggle.com/datasets/amritanshuspeaks/jud-ipl",
            "name": "Indian Legal Judgment Prediction (Jud-IPL)",
            "description": "42K+ case documents with judgment labels"
        },
    ]

    print("=" * 60)
    print("  Smart Judicial Case Timeline Analyzer")
    print("  Kaggle Dataset Downloader")
    print("=" * 60)

    for i, ds in enumerate(datasets, 1):
        print(f"\n[{i}/{len(datasets)}] Downloading: {ds['name']}")
        print(f"    Purpose: {ds['description']}")
        print(f"    URL: {ds['url']}")
        print("-" * 40)
        try:
            od.download(ds["url"], data_dir=DATA_DIR)
            print(f"    ✓ Downloaded successfully!")
        except Exception as e:
            print(f"    ✗ Error: {e}")
            print(f"    Skipping this dataset...")

    print("\n" + "=" * 60)
    print("  Download Complete!")
    print(f"  Data saved to: {DATA_DIR}")
    print("=" * 60)

    # List downloaded files
    if os.path.exists(DATA_DIR):
        print("\nDownloaded files:")
        for root, dirs, files in os.walk(DATA_DIR):
            level = root.replace(DATA_DIR, "").count(os.sep)
            indent = "  " * level
            print(f"  {indent}{os.path.basename(root)}/")
            sub_indent = "  " * (level + 1)
            for f in files[:10]:  # Show first 10 files per folder
                filepath = os.path.join(root, f)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"  {sub_indent}{f} ({size_mb:.1f} MB)")
            if len(files) > 10:
                print(f"  {sub_indent}... and {len(files) - 10} more files")


def create_sample_data():
    """Create sample data for testing without Kaggle download."""
    import database as db

    print("\nCreating sample case data for testing...")

    sample_cases = [
        {
            "case_number": "SCI/2024/001",
            "title": "State of Maharashtra vs. Sharma Industries Ltd.",
            "court": "Supreme Court of India",
            "judge": "Hon. Justice R.K. Agrawal",
            "petitioner": "State of Maharashtra",
            "respondent": "Sharma Industries Ltd.",
            "case_type": "Civil",
            "filing_date": "2024-01-15",
            "status": "Hearing",
            "priority": "High"
        },
        {
            "case_number": "SCI/2024/002",
            "title": "Union of India vs. Green Earth Foundation",
            "court": "Supreme Court of India",
            "judge": "Hon. Justice S. Patel",
            "petitioner": "Union of India",
            "respondent": "Green Earth Foundation",
            "case_type": "Environmental",
            "filing_date": "2024-02-20",
            "status": "Pending",
            "priority": "Normal"
        },
        {
            "case_number": "SCI/2023/156",
            "title": "Rajesh Kumar vs. State of Uttar Pradesh",
            "court": "Supreme Court of India",
            "judge": "Hon. Justice M. Verma",
            "petitioner": "Rajesh Kumar",
            "respondent": "State of Uttar Pradesh",
            "case_type": "Criminal",
            "filing_date": "2023-06-10",
            "status": "Disposed",
            "priority": "High"
        },
        {
            "case_number": "SCI/2024/003",
            "title": "ABC Technologies Pvt. Ltd. vs. XYZ Corp.",
            "court": "Supreme Court of India",
            "judge": "Hon. Justice A. Deshmukh",
            "petitioner": "ABC Technologies Pvt. Ltd.",
            "respondent": "XYZ Corp.",
            "case_type": "Intellectual Property",
            "filing_date": "2024-03-05",
            "status": "Pending",
            "priority": "Normal"
        },
        {
            "case_number": "SCI/2023/200",
            "title": "Workers Union vs. National Steel Corporation",
            "court": "Supreme Court of India",
            "judge": "Hon. Justice P. Banerjee",
            "petitioner": "Workers Union",
            "respondent": "National Steel Corporation",
            "case_type": "Labour",
            "filing_date": "2023-09-12",
            "status": "Hearing",
            "priority": "Normal"
        },
        {
            "case_number": "SCI/2024/010",
            "title": "Sita Devi vs. Ram Prasad",
            "court": "High Court of Delhi",
            "judge": "Hon. Justice K. Sharma",
            "petitioner": "Sita Devi",
            "respondent": "Ram Prasad",
            "case_type": "Family",
            "filing_date": "2024-04-01",
            "status": "Pending",
            "priority": "High"
        },
    ]

    for case in sample_cases:
        try:
            case_id = db.create_case(**case)
            print(f"  ✓ Created case: {case['case_number']} — {case['title']}")

            # Add sample timeline events with proper dates
            from datetime import datetime, timedelta
            filed_dt = datetime.strptime(case["filing_date"], "%Y-%m-%d")
            notice_dt = filed_dt + timedelta(days=14)

            events = [
                (case["filing_date"], "Filing", "Case Filed",
                 f"Case {case['case_number']} filed at {case['court']}"),
                (notice_dt.strftime("%Y-%m-%d"),
                 "Notice", "Notice Issued",
                 "Court notice issued to respondent"),
            ]
            if case["status"] in ("Hearing", "Disposed"):
                hearing_dt = filed_dt + timedelta(days=90)
                events.append(
                    (hearing_dt.strftime("%Y-%m-%d"), "Hearing", "First Hearing",
                     "Both parties presented initial arguments")
                )
            if case["status"] == "Disposed":
                judgment_dt = filed_dt + timedelta(days=180)
                events.append(
                    (judgment_dt.strftime("%Y-%m-%d"), "Judgment", "Final Judgment Delivered",
                     "Court delivered the final judgment in the case")
                )

            for evt in events:
                db.add_timeline_event(case_id, evt[0], evt[1], evt[2], evt[3])

        except Exception as e:
            print(f"  ✗ Case {case['case_number']} already exists or error: {e}")

    print("\n  ✓ Sample data created successfully!")


if __name__ == "__main__":
    print("Choose an option:")
    print("  1. Download Kaggle datasets")
    print("  2. Create sample data only (no download)")
    print("  3. Both (download + sample data)")

    choice = input("\nEnter choice (1/2/3): ").strip()

    if choice == "1":
        download_with_opendatasets()
    elif choice == "2":
        create_sample_data()
    elif choice == "3":
        download_with_opendatasets()
        create_sample_data()
    else:
        print("Invalid choice. Running sample data creation...")
        create_sample_data()
