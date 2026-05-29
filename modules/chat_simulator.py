"""
Live Chat Simulator Module.
Provides realistic simulated chat dialogues (safe and toxic) to showcase 
the automatic Aegis AI real-time moderation and stats updates.
"""

SIMULATED_DIALOGUES = [
    # Dialogue 0: Safe intro
    {
        "sender_id": 1,      # Aarav Sharma
        "receiver_id": 2,    # Priya Patel
        "text": "Hey Priya, did you commit the updated WebGL 3D Sentiment Constellation?",
        "is_simulated": True
    },
    # Dialogue 1: Safe response
    {
        "sender_id": 2,      # Priya Patel
        "receiver_id": 1,    # Aarav Sharma
        "text": "Yes Aarav! Added the concentric glow rings and updated the particle buffers. It streams beautifully.",
        "is_simulated": True
    },
    # Dialogue 2: Safe conversation
    {
        "sender_id": 1,      # Aarav Sharma
        "receiver_id": 2,    # Priya Patel
        "text": "Brilliant. Streamlit Cloud should load the dashboard smoothly without any browser lags now.",
        "is_simulated": True
    },
    # Dialogue 3: Toxic Insult
    {
        "sender_id": 3,      # Rohan Das
        "receiver_id": 1,    # Aarav Sharma
        "text": "Aarav, you are a stupid loser and a complete idiot! Shut up!",
        "is_simulated": True
    },
    # Dialogue 4: Safe warning
    {
        "sender_id": 2,      # Priya Patel
        "receiver_id": 3,    # Rohan Das
        "text": "Rohan, please keep the workspace respectful. There is no need for toxic language here.",
        "is_simulated": True
    },
    # Dialogue 5: Toxic Threat
    {
        "sender_id": 5,      # Kabir Singh
        "receiver_id": 2,    # Priya Patel
        "text": "Priya, stay out of this! I will find you and physically hurt you!",
        "is_simulated": True
    },
    # Dialogue 6: Safe resolve
    {
        "sender_id": 1,      # Aarav Sharma
        "receiver_id": 5,    # Kabir Singh
        "text": "Kabir, your message has been flagged by Aegis AI and sent to the Moderation Ledger.",
        "is_simulated": True
    }
]


def get_dialogue_line(index):
    """Retrieve a pre-loaded simulation message by index."""
    if index < 0 or index >= len(SIMULATED_DIALOGUES):
        return None
    return SIMULATED_DIALOGUES[index]


def get_total_dialogue_count():
    """Retrieve total count of pre-loaded simulated dialogues."""
    return len(SIMULATED_DIALOGUES)
