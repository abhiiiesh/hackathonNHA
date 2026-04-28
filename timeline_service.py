import dateparser
from datetime import datetime
from typing import List, Dict, Any

class TimelineService:
    def __init__(self):
        pass

    def construct_timeline(self, events: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Takes a list of events: [{"event_type": "Admission", "date_str": "02-Feb-26", "source": "Discharge Summary"}]
        Sorts them and validates plausibility.
        """
        parsed_events = []
        for event in events:
            # Parse the date handling messy formats
            parsed_date = dateparser.parse(event["date_str"])
            if parsed_date:
                parsed_events.append({
                    "event_type": event["event_type"],
                    "date": parsed_date,
                    "date_str": event["date_str"],
                    "source": event["source"]
                })
            else:
                parsed_events.append({
                    "event_type": event["event_type"],
                    "date": None,
                    "date_str": event["date_str"],
                    "source": event["source"],
                    "temporal_validity": "Invalid Date Format"
                })

        # Sort chronological
        valid_events = [e for e in parsed_events if e["date"] is not None]
        valid_events.sort(key=lambda x: x["date"])

        # Validate sequence
        # Expected sequence: Admission <= Investigation <= Procedure <= Discharge
        sequence_map = {"Admission": 1, "Diagnostic Investigation": 2, "Procedure": 3, "Discharge": 4}
        
        timeline_output = []
        highest_seq_seen = 0
        flags = []

        for i, event in enumerate(valid_events):
            seq_val = sequence_map.get(event["event_type"], 0)
            
            validity = "Valid"
            if seq_val > 0:
                if seq_val < highest_seq_seen:
                    validity = f"Anomaly: {event['event_type']} occurred out of order."
                    flags.append(validity)
                else:
                    highest_seq_seen = seq_val

            timeline_output.append({
                "sequence": i + 1,
                "event_type": event["event_type"],
                "date": event["date_str"],
                "source_document": event["source"],
                "temporal_validity": validity
            })

        return {
            "timeline": timeline_output,
            "flags": flags,
            "is_plausible": len(flags) == 0
        }
