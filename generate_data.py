"""
Generate comprehensive sample judicial datasets for the Smart Judicial Case Timeline Analyzer.
Creates realistic Indian court judgment data with proper legal terminology.
"""
import os
import csv
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(os.path.join(DATA_DIR, "jud-ipl"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "indian-court"), exist_ok=True)


# === Indian Supreme Court Judgments Dataset ===
COURTS = [
    "Supreme Court of India", "High Court of Delhi", "High Court of Bombay",
    "High Court of Madras", "High Court of Calcutta", "High Court of Karnataka",
    "High Court of Allahabad", "High Court of Gujarat", "High Court of Kerala",
    "High Court of Rajasthan", "High Court of Punjab and Haryana",
]

JUDGES = [
    "Justice D.Y. Chandrachud", "Justice Sanjiv Khanna", "Justice B.R. Gavai",
    "Justice Surya Kant", "Justice Aniruddha Bose", "Justice Vikram Nath",
    "Justice J.K. Maheshwari", "Justice Hima Kohli", "Justice M.M. Sundresh",
    "Justice Bela Trivedi", "Justice P.S. Narasimha", "Justice Manoj Misra",
    "Justice Ahsanuddin Amanullah", "Justice Aravind Kumar", "Justice Sanjay Kumar",
]

CASE_TYPES = ["Civil", "Criminal", "Constitutional", "Tax", "Labour", "Environmental",
              "Intellectual Property", "Family", "Consumer", "Arbitration"]

STATUSES = ["Pending", "Hearing", "Arguments", "Evidence", "Reserved", "Disposed"]
PRIORITIES = ["Normal", "High", "Urgent"]

PETITIONERS = [
    "State of Maharashtra", "Union of India", "State of Delhi", "State of Karnataka",
    "State of Tamil Nadu", "State of Uttar Pradesh", "State of Rajasthan",
    "Ravi Kumar", "Anita Sharma", "Suresh Patel", "Meena Devi",
    "Rajesh Industries Ltd.", "Tata Motors Ltd.", "Infosys Technologies",
    "ABC Corporation", "XYZ Enterprises", "National Insurance Co.",
    "Life Insurance Corporation", "Reserve Bank of India",
    "Central Bureau of Investigation", "Enforcement Directorate",
]

RESPONDENTS = [
    "Sharma Industries Ltd.", "Patel & Associates", "Kumar Construction Co.",
    "Gupta Pharmaceuticals", "Reddy Holdings", "Singh Transport",
    "Mehta Bros.", "Chopra Electronics", "Verma Steel Works",
    "Agarwal Textiles", "Nair Shipping Corp.", "Bose Engineering",
    "Jha Mining Co.", "Das Chemical Works", "Iyer Software Solutions",
    "Pandey Real Estate", "Mishra Healthcare", "Sinha Motors",
    "Bhatt Food Products", "Trivedi Constructions",
]

JUDGMENT_TEMPLATES = [
    """IN THE {court}
CASE NO. {case_number}
{petitioner} vs. {respondent}

Date of Judgment: {judgment_date}
Coram: {judge}

JUDGMENT

This is a {case_type} case filed under Section {section} of the {act}. The petitioner has approached this Hon'ble court seeking {relief}.

The facts of the case are as follows: The petitioner filed the present case on {filing_date} before this court. On {hearing_date}, both parties were heard at length. The learned counsel for the petitioner argued that {argument_pet}. The respondent's counsel contended that {argument_resp}.

After careful consideration of the arguments presented by both sides, the evidence on record, and the applicable law, this court is of the opinion that {opinion}.

In light of the above, the petition is hereby {disposition}. The parties shall bear their own costs.

ORDER
1. The {order_detail_1}.
2. The registry is directed to {order_detail_2}.
3. All pending applications, if any, stand disposed of.

Sd/-
{judge}
{court}
{judgment_date}""",
    """SUPREME COURT OF INDIA
CIVIL APPELLATE JURISDICTION
{case_number}

{petitioner}
VERSUS
{respondent}

DATE OF JUDGMENT: {judgment_date}
BENCH: {judge}

J U D G M E N T

1. This appeal has been filed challenging the judgment and order dated {hearing_date} passed by the {lower_court} in {lower_case_number}.

2. The brief facts of the case are that the appellant filed a suit under Section {section} of the {act} seeking {relief}. The trial court {trial_outcome}. Being aggrieved, the appellant preferred an appeal before the High Court which {hc_outcome}.

3. We have heard learned counsel for both parties and perused the material on record.

4. The question that falls for our consideration is whether {legal_question}.

5. After examining the contentions raised and the precedents cited, including the decision in {precedent_case}, we are of the considered view that {opinion}.

6. In the result, this appeal is {disposition}. No order as to costs.

Sd/-
{judge}""",
]

SECTIONS = ["302", "420", "498A", "376", "304B", "153A", "295A", "124A",
            "34", "120B", "307", "379", "406", "415", "467", "468", "471"]
ACTS = [
    "Indian Penal Code, 1860", "Code of Criminal Procedure, 1973",
    "Code of Civil Procedure, 1908", "Indian Contract Act, 1872",
    "Indian Evidence Act, 1872", "Constitution of India",
    "Companies Act, 2013", "Arbitration and Conciliation Act, 1996",
    "Information Technology Act, 2000", "Consumer Protection Act, 2019",
    "Motor Vehicles Act, 1988", "Negotiable Instruments Act, 1881",
    "Prevention of Corruption Act, 1988", "NDPS Act, 1985",
    "Transfer of Property Act, 1882", "Hindu Succession Act, 1956",
    "Muslim Personal Law (Shariat) Application Act, 1937",
    "Industrial Disputes Act, 1947", "Environment Protection Act, 1986",
]
RELIEFS = [
    "quashing of the FIR registered against the petitioner",
    "a writ of mandamus directing the respondent to comply with the statutory provisions",
    "compensation for the losses suffered due to breach of contract",
    "declaration that the impugned order is null and void",
    "an injunction restraining the respondent from proceeding with the construction",
    "restoration of the petitioner to the previous position with all consequential benefits",
    "setting aside the order of the lower court on grounds of jurisdictional error",
    "grant of anticipatory bail in the matter",
    "enforcement of fundamental rights under Article 21 of the Constitution",
    "relief under Section 9 of the Arbitration and Conciliation Act",
]

def random_date(start_year=2020, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def generate_case_number(idx, court):
    prefixes = {
        "Supreme Court of India": "SCI",
        "High Court of Delhi": "HCD", "High Court of Bombay": "HCB",
        "High Court of Madras": "HCM", "High Court of Calcutta": "HCC",
        "High Court of Karnataka": "HCK", "High Court of Allahabad": "HCA",
        "High Court of Gujarat": "HCG", "High Court of Kerala": "HCKL",
        "High Court of Rajasthan": "HCR", "High Court of Punjab and Haryana": "HCPH",
    }
    prefix = prefixes.get(court, "HC")
    year = random.randint(2020, 2024)
    return f"{prefix}/{year}/{idx:04d}"


# Generate cases
print("Generating cases...")
cases_data = []
for i in range(1, 51):
    court = random.choice(COURTS)
    case_num = generate_case_number(i, court)
    filing = random_date()
    status = random.choice(STATUSES)
    case_type = random.choice(CASE_TYPES)
    pet = random.choice(PETITIONERS)
    resp = random.choice(RESPONDENTS)
    judge = random.choice(JUDGES)
    priority = random.choice(PRIORITIES)
    
    cases_data.append({
        "case_number": case_num,
        "title": f"{pet} vs. {resp}",
        "court": court,
        "judge": judge,
        "petitioner": pet,
        "respondent": resp,
        "case_type": case_type,
        "filing_date": filing.strftime("%Y-%m-%d"),
        "status": status,
        "priority": priority,
    })

# Write cases CSV
cases_csv = os.path.join(DATA_DIR, "indian-court", "cases.csv")
with open(cases_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=cases_data[0].keys())
    writer.writeheader()
    writer.writerows(cases_data)
print(f"  Written {len(cases_data)} cases to {cases_csv}")


# Generate judgments
print("Generating judgments...")
judgments = []
for case in cases_data[:30]:
    filing = datetime.strptime(case["filing_date"], "%Y-%m-%d")
    hearing = filing + timedelta(days=random.randint(30, 180))
    judgment_date = hearing + timedelta(days=random.randint(7, 90))
    
    template = random.choice(JUDGMENT_TEMPLATES)
    text = template.format(
        court=case["court"],
        case_number=case["case_number"],
        petitioner=case["petitioner"],
        respondent=case["respondent"],
        judge=case["judge"],
        case_type=case["case_type"].lower(),
        filing_date=filing.strftime("%d %B %Y"),
        hearing_date=hearing.strftime("%d %B %Y"),
        judgment_date=judgment_date.strftime("%d %B %Y"),
        section=random.choice(SECTIONS),
        act=random.choice(ACTS),
        relief=random.choice(RELIEFS),
        argument_pet="the constitutional rights of the petitioner have been violated and the respondent has acted in contravention of the established legal principles",
        argument_resp="the petitioner has failed to establish a prima facie case and the present proceedings are an abuse of the process of law",
        opinion="the contentions raised by the petitioner have merit and the impugned order cannot be sustained in law",
        disposition=random.choice(["allowed", "dismissed", "partly allowed", "disposed of"]),
        order_detail_1=random.choice(["impugned order is set aside", "petition is dismissed with costs",
                                      "matter is remanded to the trial court for fresh consideration",
                                      "respondent shall comply with the directions within 30 days"]),
        order_detail_2=random.choice(["send a copy of this order to all concerned",
                                      "list the matter for compliance on the next date",
                                      "communicate this order to the lower court forthwith"]),
        lower_court=random.choice(["High Court of Delhi", "High Court of Bombay", "District Court"]),
        lower_case_number=f"WP(C) No. {random.randint(100,9999)}/{random.randint(2020,2024)}",
        trial_outcome=random.choice(["decreed the suit in favour of the plaintiff",
                                      "dismissed the suit on merits",
                                      "allowed the application"]),
        hc_outcome=random.choice(["upheld the order of the trial court",
                                   "reversed the order of the trial court",
                                   "modified the order partially"]),
        legal_question=random.choice([
            "the lower court erred in interpreting the provisions of the statute",
            "the principles of natural justice were violated",
            "the evidence on record supports the findings of the trial court",
        ]),
        precedent_case=random.choice([
            "Maneka Gandhi v. Union of India (1978) 1 SCC 248",
            "Kesavananda Bharati v. State of Kerala (1973) 4 SCC 225",
            "Vishaka v. State of Rajasthan (1997) 6 SCC 241",
            "S.R. Bommai v. Union of India (1994) 3 SCC 1",
            "K.S. Puttaswamy v. Union of India (2017) 10 SCC 1",
        ]),
    )
    
    judgments.append({
        "case_number": case["case_number"],
        "court": case["court"],
        "judge": case["judge"],
        "judgment_date": judgment_date.strftime("%Y-%m-%d"),
        "petitioner": case["petitioner"],
        "respondent": case["respondent"],
        "case_type": case["case_type"],
        "judgment_text": text,
        "word_count": len(text.split()),
    })

# Write judgments CSV
judgments_csv = os.path.join(DATA_DIR, "indian-court", "judgments.csv")
with open(judgments_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=judgments[0].keys())
    writer.writeheader()
    writer.writerows(judgments)
print(f"  Written {len(judgments)} judgments to {judgments_csv}")


# === Jud-IPL Dataset (Indian Patent Law) ===
print("Generating IPL dataset...")
ipl_cases = []
ipl_categories = ["Patent Infringement", "Patent Validity", "Compulsory Licensing",
                   "Patent Opposition", "Patent Revocation", "Trade Secret"]

for i in range(1, 31):
    filing = random_date(2019, 2024)
    ipl_cases.append({
        "case_id": i,
        "case_number": f"CS(COMM) {random.randint(100,999)}/{filing.year}",
        "title": f"{random.choice(PETITIONERS)} vs. {random.choice(RESPONDENTS)}",
        "court": random.choice(["High Court of Delhi", "High Court of Bombay", "High Court of Madras", "High Court of Calcutta"]),
        "category": random.choice(ipl_categories),
        "filing_date": filing.strftime("%Y-%m-%d"),
        "status": random.choice(STATUSES),
        "patent_number": f"IN{random.randint(200000,999999)}",
        "technology_area": random.choice(["Pharmaceutical", "Software", "Mechanical",
                                          "Chemical", "Biotechnology", "Electronics"]),
        "outcome": random.choice(["Infringement Found", "No Infringement", "Patent Invalid",
                                   "Settled", "Pending", "Injunction Granted"]),
    })

ipl_csv = os.path.join(DATA_DIR, "jud-ipl", "ipl_cases.csv")
with open(ipl_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=ipl_cases[0].keys())
    writer.writeheader()
    writer.writerows(ipl_cases)
print(f"  Written {len(ipl_cases)} IPL cases to {ipl_csv}")


# === Summary ===
print("\n=== Dataset Generation Complete ===")
for root, dirs, files in os.walk(DATA_DIR):
    for fname in files:
        fpath = os.path.join(root, fname)
        size = os.path.getsize(fpath)
        print(f"  {os.path.relpath(fpath, DATA_DIR)} ({size/1024:.1f} KB)")
print("\nDone!")
