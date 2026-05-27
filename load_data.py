"""Load generated CSV data into the SQLite database."""
import os
import csv
import database as db

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
cases_csv = os.path.join(DATA_DIR, "indian-court", "cases.csv")
judgments_csv = os.path.join(DATA_DIR, "indian-court", "judgments.csv")
ipl_csv = os.path.join(DATA_DIR, "jud-ipl", "ipl_cases.csv")

# Wipe DB first
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "judicial.db")
if os.path.exists(db_path):
    os.remove(db_path)
db.init_db()
print("Wiped and re-initialized database.")

# Load Indian Court Cases
case_id_map = {} # Maps case_number to database case_id
if os.path.exists(cases_csv):
    with open(cases_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                case_id = db.create_case(
                    row['case_number'], row['title'], row['court'], row['judge'],
                    row['petitioner'], row['respondent'], row['case_type'],
                    row['filing_date'], row['status'], row.get('priority', 'Normal')
                )
                case_id_map[row['case_number']] = case_id
                
                # Add filing event
                db.add_timeline_event(case_id, row['filing_date'], "Filing", "Case Filed", f"Filed at {row['court']}")
            except Exception as e:
                print(f"Error adding case {row['case_number']}: {e}")
    print(f"Loaded {len(case_id_map)} basic cases.")

# Load IPL Cases
if os.path.exists(ipl_csv):
    with open(ipl_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                # Need to map CSV columns to DB expected columns
                case_id = db.create_case(
                    row['case_number'], row['title'], row['court'], "",
                    row['title'].split("vs.")[0].strip() if "vs." in row['title'] else "",
                    row['title'].split("vs.")[1].strip() if "vs." in row['title'] else "",
                    "Intellectual Property", row['filing_date'], row['status'], "Normal"
                )
                case_id_map[row['case_number']] = case_id
                db.add_timeline_event(case_id, row['filing_date'], "Filing", "Patent Case Filed", f"Patent: {row['patent_number']} ({row['category']})")
                count += 1
            except Exception as e:
                print(f"Error adding IPL case {row['case_number']}: {e}")
    print(f"Loaded {count} IPL cases.")

# Load Judgments/Documents
if os.path.exists(judgments_csv):
    with open(judgments_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            case_id = case_id_map.get(row['case_number'])
            if case_id:
                # Save as a document
                doc_name = f"Judgment_{row['case_number'].replace('/', '_')}.txt"
                db.save_document(
                    case_id, doc_name, doc_name, ".txt", 
                    row['judgment_text'], 100.0, int(row['word_count'])
                )
                db.add_timeline_event(case_id, row['judgment_date'], "Judgment", "Judgment Delivered", f"Judgment by {row['judge']}")
                
                # Update status of this case to Disposed
                db.update_case_status(case_id, "Disposed")
                count += 1
    print(f"Loaded {count} full judgments.")

print("\nDatabase fully populated with generated realistic datasets.")
