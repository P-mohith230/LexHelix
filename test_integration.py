"""
Integration Test Suite for Cyberbullying App WhatsApp.
Validates database schemas, AI moderation classification metrics,
profile behavioral counters, and auto-delete censorship pipelines.
"""

import sys
import os
import time
from datetime import datetime

# Add root directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database as db
from modules.moderator_engine import classify_message
from modules.case_flow import determine_case_stage, CASE_STAGES

# Logging colors
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
    print(f"{COLOR_YELLOW}Starting Aegis Chat Real-Time Shield Verification Suite...{COLOR_RESET}")
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
    log_test_header("1. SQLite Database Schema & Contact Seeding")
    
    try:
        contacts = db.get_all_contacts()
        assert_test(len(contacts) > 0, f"Database seeded with {len(contacts)} default contacts")
        
        # Test contact creation
        test_contact_name = f"Test User {datetime.now().microsecond}"
        contact_id = db.create_contact(test_contact_name, "🤖", 0.0, 0, 0, 1)
        assert_test(contact_id > 0, f"Successfully created new contact record (ID: {contact_id})")
        
        # Verify retrieval
        contact = db.get_contact(contact_id)
        assert_test(contact is not None, "Successfully retrieved contact from database")
        assert_test(contact["name"] == test_contact_name, f"Contact name matches: {contact['name']}")
        assert_test(contact["sent_bully_count"] == 0, "Initial sent toxicity count is zero")
        assert_test(contact["received_bully_count"] == 0, "Initial received toxicity count is zero")
        
    except Exception as e:
        assert_test(False, f"Database Operations raised exception: {str(e)}")

    # ----------------------------------------------------------
    #  2. AI MODERATION CLASSIFICATION ACCURACY
    # ----------------------------------------------------------
    log_test_header("2. AI Moderation Engine Classification Heuristics")
    
    try:
        # Test Case A: Extreme Threat
        threat_msg = "I will find you and physically hurt you"
        res_a = classify_message(threat_msg)
        assert_test(res_a["is_toxic"], "Flagged extreme threat as toxic")
        assert_test(res_a["classification_tag"] == "Threat", f"Classified accurately as Threat (Score: {res_a['toxicity_probability']})")
        
        # Test Case B: Direct Insult
        insult_msg = "You are a stupid pathetic loser"
        res_b = classify_message(insult_msg)
        assert_test(res_b["is_toxic"], "Flagged insult as toxic")
        assert_test(res_b["classification_tag"] == "Insult", f"Classified accurately as Insult (Score: {res_b['toxicity_probability']})")
        
        # Test Case C: Benign Conversation
        safe_msg = "Hey, are we still pairing on the WebGL visualizations today?"
        res_c = classify_message(safe_msg)
        assert_test(not res_c["is_toxic"], "Verified safe message is not toxic")
        assert_test(res_c["classification_tag"] == "Safe", f"Classified accurately as Safe (Score: {res_c['toxicity_probability']})")
        
    except Exception as e:
        assert_test(False, f"Moderation Engine raised exception: {str(e)}")

    # ----------------------------------------------------------
    #  3. PROFILE BEHAVIORAL METRICS ACCURACY
    # ----------------------------------------------------------
    log_test_header("3. User Profile Toxicity Stats Tracking")
    
    try:
        sender_id = 1  # Aarav Sharma
        receiver_id = contact_id  # Our newly created test contact
        
        # Aarav sends a toxic message to receiver
        toxic_text = "Get lost, you pathetic spammer!"
        mod_res = classify_message(toxic_text)
        
        msg_id = db.save_message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_text=toxic_text,
            original_text=toxic_text,
            is_toxic=1 if mod_res["is_toxic"] else 0,
            toxicity_probability=mod_res["toxicity_probability"],
            classification_tag=mod_res["classification_tag"]
        )
        assert_test(msg_id > 0, f"Saved toxic message successfully (ID: {msg_id})")
        
        # Simulate timer countdown execution & update statistics
        # Increments sent stats on sender, received stats on receiver
        db.increment_contact_stats(sender_id, "sent")
        db.increment_contact_stats(receiver_id, "received")
        
        # Verify stats changes in database
        sender = db.get_contact(sender_id)
        receiver = db.get_contact(receiver_id)
        
        assert_test(sender["sent_bully_count"] > 0, f"Sender's 'sent_bully_count' successfully incremented: {sender['sent_bully_count']}")
        assert_test(receiver["received_bully_count"] > 0, f"Receiver's 'received_bully_count' successfully incremented: {receiver['received_bully_count']}")
        assert_test(sender["toxicity_score"] > 0.0, f"Sender's composite toxicity index recalculated: {int(sender['toxicity_score']*100)}%")
        
    except Exception as e:
        assert_test(False, f"Toxicity Stats Tracking raised exception: {str(e)}")

    # ----------------------------------------------------------
    #  4. AUTO-DELETE CENSOR MECHANISM
    # ----------------------------------------------------------
    log_test_header("4. 10-Second Auto-Delete Censor Flow")
    
    try:
        # Censor the toxic message permanently in DB
        placeholder_text = "[Message deleted - flagged as cyberbullying]"
        db.flag_message_deleted(msg_id, placeholder_text)
        
        # Retrieve message and verify contents
        censored_msg = None
        history = db.get_chat_history(sender_id, receiver_id)
        for m in history:
            if m["message_id"] == msg_id:
                censored_msg = m
                break
                
        assert_test(censored_msg is not None, "Retrieved censored message from history")
        assert_test(censored_msg["is_deleted"] == 1, "Censor deleted flag set to 1")
        assert_test(censored_msg["message_text"] == placeholder_text, f"Message content successfully cleared and replaced with: {censored_msg['message_text']}")
        assert_test(censored_msg["original_text"] == toxic_text, "Original text preserved for audit records")
        
    except Exception as e:
        assert_test(False, f"Censor Mechanism raised exception: {str(e)}")

    # ----------------------------------------------------------
    #  5. MODERATION LEDGER & AUDIT
    # ----------------------------------------------------------
    log_test_header("5. Moderation Audit Ledger Persistence")
    
    try:
        # Save alert log
        alert_id = db.save_moderation_alert(
            message_id=msg_id,
            rule_triggered="Toxicity limit breached: Insult",
            severity="Medium",
            action_taken="Censored & Deleted"
        )
        assert_test(alert_id > 0, f"Successfully created audit alert (ID: {alert_id})")
        
        # Verify ledger retrieval
        alerts = db.get_all_alerts()
        assert_test(len(alerts) > 0, "Audited logs successfully retrieved from database")
        
        # Clean up database
        db.delete_contact(contact_id) # cascading cleanup test user
        assert_test(db.get_contact(contact_id) is None, "Successfully cleaned up integration test contacts")
        
    except Exception as e:
        assert_test(False, f"Ledger Persistence raised exception: {str(e)}")

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
        print(f"\n{COLOR_GREEN}* CONGRATULATIONS! Cyberbullying App WhatsApp is verified 100% stable! *{COLOR_RESET}\n")
        return 0
    else:
        print(f"\n{COLOR_RED}! INTEGRATION TEST FAILURE: Subsystem errors detected. !{COLOR_RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_integration_tests())
