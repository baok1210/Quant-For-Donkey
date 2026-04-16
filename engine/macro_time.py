"""
Macro Time Filter - London Open, NY Open, Killzones
Timezone: Vietnam (UTC+7)
"""

from datetime import datetime, time
from typing import Dict, List
import pytz


class MacroTimeFilter:
    """
    Bộ lọc thời gian cho các phiên giao dịch quan trọng
    Timezone: Indochina Time (ICT - UTC+7)
    """

    def __init__(self, tz: str = "Asia/Ho_Chi_Minh"):
        self.tz = pytz.timezone(tz)

        self.sessions = {
            "LONDON_OPEN": {
                "start": time(14, 0),
                "end": time(15, 0),
                "description": "London Session Open",
            },
            "LONDON_KILLZONE": {
                "start": time(14, 0),
                "end": time(16, 0),
                "description": "London Killzone",
            },
            "NY_OPEN": {
                "start": time(20, 30),
                "end": time(21, 30),
                "description": "New York Session Open",
            },
            "NY_KILLZONE": {
                "start": time(20, 0),
                "end": time(23, 0),
                "description": "NY Killzone",
            },
            "OVERLAP_LONDON_NY": {
                "start": time(20, 0),
                "end": time(21, 0),
                "description": "London-NY Overlap",
            },
        }

    def get_current_time_ict(self) -> datetime:
        return datetime.now(self.tz)

    def is_in_session(self, session_name: str, current_time: datetime = None) -> bool:
        if current_time is None:
            current_time = self.get_current_time_ict()

        if session_name not in self.sessions:
            return False

        session = self.sessions[session_name]
        return session["start"] <= current_time.time() <= session["end"]

    def get_active_sessions(self, current_time: datetime = None) -> List[str]:
        if current_time is None:
            current_time = self.get_current_time_ict()

        active = []
        for session_name in self.sessions:
            if self.is_in_session(session_name, current_time):
                active.append(session_name)
        return active

    def is_trade_allowed(self) -> Dict:
        current = self.get_current_time_ict()
        active_sessions = self.get_active_sessions(current)

        allowed_sessions = [
            "LONDON_OPEN",
            "LONDON_KILLZONE",
            "NY_OPEN",
            "NY_KILLZONE",
            "OVERLAP_LONDON_NY",
        ]
        is_allowed = len([s for s in active_sessions if s in allowed_sessions]) > 0

        return {
            "allowed": is_allowed,
            "current_time_ict": current.strftime("%Y-%m-%d %H:%M:%S"),
            "active_sessions": active_sessions,
            "in_killzone": "LONDON_KILLZONE" in active_sessions
            or "NY_KILLZONE" in active_sessions,
        }


def get_macro_time_status() -> Dict:
    filter = MacroTimeFilter()
    return filter.is_trade_allowed()
