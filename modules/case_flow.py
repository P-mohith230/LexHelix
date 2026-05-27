"""
Module 3: Case Flow Analyzer
Analyzes case progression, generates timeline events, and computes court statistics.
"""

import re
from datetime import datetime, timedelta
from collections import Counter

try:
    from dateutil import parser as date_parser
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False


# ── Case Stage Definitions ─────────────────────────────────

CASE_STAGES = [
    {"stage": "Filed", "icon": "📄", "color": "#3498db"},
    {"stage": "Notice Issued", "icon": "📨", "color": "#9b59b6"},
    {"stage": "First Hearing", "icon": "🏛️", "color": "#e67e22"},
    {"stage": "Arguments", "icon": "⚖️", "color": "#f39c12"},
    {"stage": "Evidence", "icon": "📋", "color": "#1abc9c"},
    {"stage": "Reserved for Judgment", "icon": "⏳", "color": "#e74c3c"},
    {"stage": "Judgment Delivered", "icon": "📜", "color": "#2ecc71"},
    {"stage": "Disposed", "icon": "✅", "color": "#27ae60"},
]

EVENT_TYPE_COLORS = {
    "Filing": "#3498db",
    "Notice": "#9b59b6",
    "Hearing": "#e67e22",
    "Arguments": "#f39c12",
    "Evidence": "#1abc9c",
    "Order": "#e74c3c",
    "Judgment": "#2ecc71",
    "Adjournment": "#95a5a6",
    "Misc": "#7f8c8d",
}


# ── Date Extraction from Text ──────────────────────────────

def extract_dates_from_text(text):
    """Extract dates found in legal text."""
    dates = []

    patterns = [
        (r'(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{4})', 'dmy'),
        (r'(\d{4})-(\d{2})-(\d{2})', 'ymd'),
        (r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|'
         r'September|October|November|December)\s+(\d{4})', 'dMy'),
        (r'(January|February|March|April|May|June|July|August|'
         r'September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', 'Mdy'),
    ]

    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    for pattern, fmt in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                groups = match.groups()
                if fmt == 'dmy':
                    d, m, y = int(groups[0]), int(groups[1]), int(groups[2])
                elif fmt == 'ymd':
                    y, m, d = int(groups[0]), int(groups[1]), int(groups[2])
                elif fmt == 'dMy':
                    d = int(groups[0])
                    m = month_map.get(groups[1].lower(), 1)
                    y = int(groups[2])
                elif fmt == 'Mdy':
                    m = month_map.get(groups[0].lower(), 1)
                    d = int(groups[1])
                    y = int(groups[2])
                else:
                    continue

                dt = datetime(y, m, d)
                if 1900 <= y <= 2030:
                    dates.append(dt.strftime('%Y-%m-%d'))
            except (ValueError, IndexError):
                continue

    return sorted(set(dates))


# ── Timeline Generation ───────────────────────────────────

def generate_timeline_from_text(text, case_data=None):
    """
    Generate timeline events by analyzing text and case metadata.

    Returns list of timeline event dicts.
    """
    events = []
    dates_found = extract_dates_from_text(text)

    # Map keywords to event types
    keyword_event_map = {
        'filed': ('Filing', 'Case Filed'),
        'registered': ('Filing', 'Case Registered'),
        'notice': ('Notice', 'Notice Issued'),
        'summon': ('Notice', 'Summons Issued'),
        'hearing': ('Hearing', 'Hearing Conducted'),
        'heard': ('Hearing', 'Matter Heard'),
        'argued': ('Arguments', 'Arguments Presented'),
        'argument': ('Arguments', 'Arguments Phase'),
        'evidence': ('Evidence', 'Evidence Presented'),
        'witness': ('Evidence', 'Witness Examined'),
        'order': ('Order', 'Court Order Passed'),
        'directed': ('Order', 'Court Direction Issued'),
        'judgment': ('Judgment', 'Judgment Delivered'),
        'verdict': ('Judgment', 'Verdict Pronounced'),
        'dismissed': ('Judgment', 'Case Dismissed'),
        'allowed': ('Judgment', 'Appeal Allowed'),
        'disposed': ('Judgment', 'Case Disposed'),
        'adjourned': ('Adjournment', 'Case Adjourned'),
        'postponed': ('Adjournment', 'Hearing Postponed'),
    }

    text_lower = text.lower()
    sentences = re.split(r'(?<=[.!?])\s+', text)

    for sent in sentences:
        sent_lower = sent.lower()
        sent_dates = extract_dates_from_text(sent)

        for keyword, (event_type, title) in keyword_event_map.items():
            if keyword in sent_lower and sent_dates:
                events.append({
                    "event_date": sent_dates[0],
                    "event_type": event_type,
                    "title": title,
                    "description": sent.strip()[:200],
                    "color": EVENT_TYPE_COLORS.get(event_type, "#7f8c8d")
                })
                break

    # Add case metadata events
    if case_data:
        if case_data.get("filing_date"):
            events.insert(0, {
                "event_date": case_data["filing_date"],
                "event_type": "Filing",
                "title": "Case Filed",
                "description": f"Case {case_data.get('case_number', '')} filed at {case_data.get('court', 'Court')}",
                "color": EVENT_TYPE_COLORS["Filing"]
            })

    # Deduplicate by date+type
    seen = set()
    unique_events = []
    for evt in events:
        key = (evt["event_date"], evt["event_type"])
        if key not in seen:
            seen.add(key)
            unique_events.append(evt)

    return sorted(unique_events, key=lambda x: x["event_date"])


# ── Case Flow Status Determination ─────────────────────────

def determine_case_stage(events):
    """Determine current case stage from timeline events."""
    if not events:
        return CASE_STAGES[0]

    event_types = [e.get("event_type", "") for e in events]

    # Check from latest stage backwards
    stage_map = {
        "Disposed": 7,
        "Judgment": 6,
        "Order": 5,
        "Evidence": 4,
        "Arguments": 3,
        "Hearing": 2,
        "Notice": 1,
        "Filing": 0,
    }

    max_stage = 0
    for et in event_types:
        if et in stage_map:
            max_stage = max(max_stage, stage_map[et])

    return CASE_STAGES[min(max_stage, len(CASE_STAGES) - 1)]


# ── Statistics Computation ─────────────────────────────────

def compute_case_statistics(cases, timeline_events_map=None):
    """
    Compute court-wide statistics from cases data.

    Args:
        cases: List of case dicts.
        timeline_events_map: Dict of case_id -> list of timeline events.

    Returns:
        Dict with computed statistics.
    """
    if not cases:
        return {
            "total_cases": 0,
            "status_distribution": {},
            "type_distribution": {},
            "avg_duration_days": 0,
            "court_distribution": {},
            "priority_distribution": {},
            "monthly_trend": {},
        }

    stats = {
        "total_cases": len(cases),
        "status_distribution": dict(Counter(c.get("status", "Unknown") for c in cases)),
        "type_distribution": dict(Counter(c.get("case_type", "Unknown") for c in cases)),
        "court_distribution": dict(Counter(c.get("court", "Unknown") for c in cases)),
        "priority_distribution": dict(Counter(c.get("priority", "Normal") for c in cases)),
    }

    # Calculate average case duration
    durations = []
    for case in cases:
        if case.get("filing_date") and case.get("status") == "Disposed":
            try:
                filed = datetime.strptime(case["filing_date"], "%Y-%m-%d")
                updated = datetime.strptime(
                    case.get("updated_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "%Y-%m-%d %H:%M:%S"
                )
                duration = (updated - filed).days
                if duration > 0:
                    durations.append(duration)
            except (ValueError, TypeError):
                pass

    stats["avg_duration_days"] = round(sum(durations) / len(durations)) if durations else 0

    # Monthly filing trend
    monthly = Counter()
    for case in cases:
        if case.get("filing_date"):
            try:
                dt = datetime.strptime(case["filing_date"], "%Y-%m-%d")
                month_key = dt.strftime("%Y-%m")
                monthly[month_key] += 1
            except (ValueError, TypeError):
                pass
    stats["monthly_trend"] = dict(sorted(monthly.items()))

    return stats


# ── Vis-Timeline Format Converter ──────────────────────────

def events_to_vis_timeline(events, case_title=""):
    """
    Convert events to vis-timeline JSON format.
    Compatible with streamlit-timeline component.
    """
    timeline_items = []
    for i, evt in enumerate(events):
        timeline_items.append({
            "id": i + 1,
            "content": f"{evt.get('title', 'Event')}",
            "start": evt["event_date"],
            "type": "box",
            "style": f"background-color: {evt.get('color', '#3498db')}; color: white; border-radius: 4px;",
            "title": evt.get("description", ""),
        })

    return {
        "title": {
            "text": {"headline": case_title or "Case Timeline", "text": ""},
        },
        "events": [
            {
                "start_date": {
                    "year": evt["event_date"].split("-")[0],
                    "month": evt["event_date"].split("-")[1] if len(evt["event_date"].split("-")) > 1 else "1",
                    "day": evt["event_date"].split("-")[2] if len(evt["event_date"].split("-")) > 2 else "1",
                },
                "text": {
                    "headline": evt.get("title", "Event"),
                    "text": evt.get("description", ""),
                },
                "media": {
                    "url": "",
                    "caption": evt.get("event_type", ""),
                },
            }
            for evt in events
        ] if events else []
    }
