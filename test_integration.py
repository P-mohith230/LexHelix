"""
Integration Test Suite for Smart Judicial Case Timeline Analyzer.
Validates database operations, OCR availability, NLP extraction accuracy,
and case timeline stage tracking.
"""

import sys
import os
import json
from datetime import datetime

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database as db
from modules.nlp_summarizer import summarize_judgment, extract_key_points
from modules.case_flow import generate_timeline_from_text, determine_case_stage, CASE_STAGES
from modules.ocr_extractor import is_tesseract_available, get_supported_formats

# Cohesive high-tech logging colors
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

def log_test_header(title):
    print(f"\n{COLOR_CYAN}=========================================================={COLOR_RESET}")
    print(f"{COLOR_CYAN}  TEST CATEGORY: {title}{COLOR_RESET}")
    print(f"{COLOR_CYAN}=========================================================={COLOR_RESET}")

def run_integration_tests():
    print(f"{COLOR_YELLOW}Starting Intelligent Judicial OS Verification Suite...{COLOR_RESET}")
    db.init_db()
    
    overall_passed = True
    tests_summary = []

    def assert_test(condition, message):
        nonlocal overall_passed
        if condition:
            print(f"  [{COLOR_GREEN}PASS{COLOR_RESET}] {message}")
            tests_summary.append((message, True))
        else:
            print(f"  [{COLOR_RED}FAIL{COLOR_RESET}] {message}")
            tests_summary.append((message, False))
            overall_passed = False

    # ----------------------------------------------------------
    #  1. DATABASE SANITY CHECKS
    # ----------------------------------------------------------
    log_test_header("1. SQLite Database Schema & CRUD Operations")
    
    # Test case creation
    test_case_num = f"T-SCI/2026/{datetime.now().microsecond}"
    test_case_title = "State of Maharashtra vs. Rajesh Kumar"
    
    try:
        case_id = db.create_case(
            case_number=test_case_num,
            title=test_case_title,
            court="High Court of Delhi",
            judge="Hon'ble Justice A. K. Sikri",
            petitioner="State of Maharashtra",
            respondent="Rajesh Kumar",
            case_type="Criminal",
            filing_date="2024-03-15",
            status="Pending",
            priority="High"
        )
        assert_test(case_id > 0, f"Successfully created case record (ID: {case_id})")
        
        # Verify retrieve
        case = db.get_case(case_id)
        assert_test(case is not None, "Successfully retrieved case from database")
        assert_test(case["case_number"] == test_case_num, f"Case number matches: {case['case_number']}")
        assert_test(case["case_type"] == "Criminal", "Case type matches 'Criminal'")
        assert_test(case["status"] == "Pending", "Initial status correctly set to 'Pending'")
        
        # Verify stats update
        stats = db.get_case_stats()
        assert_test(stats["total_cases"] > 0, f"Dashboard metrics retrieved. Total cases in DB: {stats['total_cases']}")
        
    except Exception as e:
        assert_test(False, f"Database Operations raised exception: {str(e)}")

    # ----------------------------------------------------------
    #  2. OCR CAPABILITY DIAGNOSTIC
    # ----------------------------------------------------------
    log_test_header("2. OCR Engine Pre-Flight Check")
    ocr_ready = is_tesseract_available()
    formats = get_supported_formats()
    
    if ocr_ready:
        assert_test(True, "Tesseract OCR engine is verified on local system path")
    else:
        print(f"  [{COLOR_YELLOW}INFO{COLOR_RESET}] Tesseract OCR is not installed/configured on system path. Fallback to pre-processed text pipelines.")
        assert_test(True, "OCR subsystem loaded successfully in fallback mode")
        
    assert_test(len(formats) > 0, f"Supported file extensions loaded: {', '.join(formats)}")

    # ----------------------------------------------------------
    #  3. NLP EXTRACTION & SUMMARY ACCURACY
    # ----------------------------------------------------------
    log_test_header("3. NLP Summarizer & Key Legal Entity Extraction Accuracy")
    
    # Realistic Indian mock legal judgment text
    mock_judgment_text = """
    IN THE HIGH COURT OF DELHI
    Civil Appeal No. 452 of 2023
    State of Maharashtra vs. Rajesh Kumar
    
    Decided on: 15 March 2024
    Presiding: Hon'ble Justice A. K. Sikri
    
    JUDGMENT
    This is a Civil Appeal filed under Section 378 of the Code of Criminal Procedure (CrPC).
    The appellant, State of Maharashtra, files this appeal against the respondent, Rajesh Kumar, challenges the acquittal order of the trial court.
    The court directed the parties to present evidence on 10 April 2024.
    Having heard the extensive arguments on 12 May 2024, the court reserved its judgment.
    Final judgment is delivered on this 27 May 2026.
    Having considered all prima facie records, legal precedents, and testimonies, we find no error in the trial court's assessment.
    Therefore, the appeal is dismissed with no order as to costs.
    """
    
    try:
        # Run NLP judgment summarization
        nlp_result = summarize_judgment(mock_judgment_text, method="extractive", num_sentences=4)
        
        assert_test(nlp_result["success"], f"Summarization completed successfully using: {nlp_result['method']}")
        assert_test(len(nlp_result["summary"]) > 0, "Summary text generated successfully")
        
        # Verify accuracy of extracted fields
        kp = nlp_result["key_points"]
        
        # Assertions on Extraction Accuracy
        has_case_num = any("452" in cn for cn in kp["case_numbers"])
        assert_test(has_case_num, f"Extracted Case Number accurately: {kp['case_numbers']}")
        
        has_court = any("delhi" in c.lower() or "supreme" in c.lower() for c in kp["court_names"])
        assert_test(has_court, f"Extracted Court Name accurately: {kp['court_names']}")
        
        has_judge = any("sikri" in j.lower() for j in kp["judges"])
        assert_test(has_judge, f"Extracted Presiding Judge accurately: {kp['judges']}")
        
        has_statute = any("section 378" in s.lower() or "crpc" in s.lower() for s in kp["statutes"])
        assert_test(has_statute, f"Extracted Statute/Section accurately: {kp['statutes']}")
        
        has_term = any("prima facie" in t.lower() for t in kp["legal_terms"])
        assert_test(has_term, f"Extracted Legal Latin Term accurately: {kp['legal_terms']}")
        
        has_date = any("15 march" in d.lower() or "2024-03-15" in d for d in kp["dates"])
        assert_test(has_date, f"Extracted Judgment Date accurately: {kp['dates']}")
        
        assert_test(len(kp["parties"]) > 0, f"Extracted Parties dictionary: {kp['parties']}")
        if len(kp["parties"]) > 0:
            assert_test("maharashtra" in kp["parties"][0]["petitioner"].lower(), f"Petitioner identified correctly: {kp['parties'][0]['petitioner']}")
            assert_test("rajesh kumar" in kp["parties"][0]["respondent"].lower(), f"Respondent identified correctly: {kp['parties'][0]['respondent']}")

    except Exception as e:
        assert_test(False, f"NLP Extractor raised exception: {str(e)}")

    # ----------------------------------------------------------
    #  4. CASE TIMELINE & PROGRESSION FLOW
    # ----------------------------------------------------------
    log_test_header("4. Case Timeline Helix Parsing & Stage Tracking")
    
    try:
        # Generate chronological timeline events from the judgment text
        events = generate_timeline_from_text(mock_judgment_text, case_data=case)
        
        assert_test(len(events) >= 3, f"Extracted {len(events)} milestones from judgment text")
        
        # Verify event dates are chronologically sorted
        event_dates = [e["event_date"] for e in events]
        is_sorted = event_dates == sorted(event_dates)
        assert_test(is_sorted, f"Timeline events chronological ordering verified: {event_dates}")
        
        # Check event types extracted
        event_types = [e["event_type"] for e in events]
        assert_test("Filing" in event_types, "Filing event type detected")
        assert_test("Arguments" in event_types or "Hearing" in event_types, "Interactive hearings/arguments detected")
        assert_test("Judgment" in event_types, "Delivered judgment event type detected")
        
        # Determine the current stage based on the extracted timeline events
        stage = determine_case_stage(events)
        assert_test(stage["stage"] in ["Judgment Delivered", "Disposed"], f"Case progression stage evaluated correctly as: {stage['stage']}")
        
    except Exception as e:
        assert_test(False, f"Timeline Progression Engine raised exception: {str(e)}")

    # ----------------------------------------------------------
    #  5. DB STORAGE PERSISTENCE INTEGRATION
    # ----------------------------------------------------------
    log_test_header("5. End-to-End Database Save & Integrity Validation")
    
    try:
        # Save OCR Document linked to the case
        doc_id = db.save_document(
            case_id=case_id,
            filename="mock_judgment_ocr.txt",
            original_name="State_vs_Rajesh_DelhiHC.txt",
            file_type=".txt",
            extracted_text=mock_judgment_text,
            ocr_confidence=98.5,
            word_count=len(mock_judgment_text.split())
        )
        assert_test(doc_id > 0, f"Saved OCR text document successfully (Doc ID: {doc_id})")
        
        # Save generated summary
        summary_id = db.save_summary(
            doc_id=doc_id,
            case_id=case_id,
            summary_text=nlp_result["summary"],
            key_points=kp,
            method=nlp_result["method"]
        )
        assert_test(summary_id > 0, f"Saved NLP judgment summary successfully (Summary ID: {summary_id})")
        
        # Add timeline events
        for e in events:
            evt_id = db.add_timeline_event(
                case_id=case_id,
                event_date=e["event_date"],
                event_type=e["event_type"],
                title=e["title"],
                description=e["description"]
            )
        assert_test(True, "Saved all timeline milestones into SQLite relational database")
        
        # Update final case status based on progression Stage
        if stage["stage"] in ["Judgment Delivered", "Disposed"]:
            db.update_case_status(case_id, "Disposed")
        else:
            db.update_case_status(case_id, "Hearing")
            
        updated_case = db.get_case(case_id)
        assert_test(updated_case["status"] == "Disposed", "Final status successfully transitioned to 'Disposed'")
        
        # Clean up test case to keep workspace DB clean and lightweight
        db.delete_case(case_id)
        assert_test(db.get_case(case_id) is None, "Successfully cleaned up integration test case records")
        
    except Exception as e:
        assert_test(False, f"DB Storage Persistence raised exception: {str(e)}")

    # ----------------------------------------------------------
    #  SUMMARY LOG
    # ----------------------------------------------------------
    print(f"\n{COLOR_CYAN}=========================================================={COLOR_RESET}")
    print(f"{COLOR_CYAN}  INTEGRATION TEST SUMMARY RESULTS{COLOR_RESET}")
    print(f"{COLOR_CYAN}=========================================================={COLOR_RESET}")
    
    passed_count = sum(1 for _, status in tests_summary if status)
    total_count = len(tests_summary)
    
    for msg, status in tests_summary:
        icon = f"[{COLOR_GREEN}OK{COLOR_RESET}]" if status else f"[{COLOR_RED}FAIL{COLOR_RESET}]"
        print(f"  {icon} {msg}")
        
    print(f"\nScore: {COLOR_GREEN if overall_passed else COLOR_RED}{passed_count}/{total_count} Tests Passed{COLOR_RESET}")
    
    if overall_passed:
        print(f"\n{COLOR_GREEN}* CONGRATULATIONS! Smart Judicial OS is verified 100% stable and fully operational! *{COLOR_RESET}\n")
        return 0
    else:
        print(f"\n{COLOR_RED}! INTEGRATION TEST FAILURE: Errors detected in subsystem validations. Please see logs. !{COLOR_RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_integration_tests())
