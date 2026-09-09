# Time Utilities - Session and timezone handling

from datetime import datetime, timedelta
import pytz
from typing import Tuple


class TimeUtils:
    """
    Utilities for timezone and trading session management.
    
    Handles:
    - UTC and session time conversions
    - Daylight Saving Time (DST) transitions
    - Trading session detection
    - Time filtering
    """
    
    # Trading sessions in UTC (approximate, accounting for DST)
    SESSIONS = {
        "london": {"start": 8, "end": 17},      # 08:00-17:00 UTC
        "newyork": {"start": 13, "end": 22},    # 13:00-22:00 UTC
        "tokyo": {"start": 21, "end": 6},       # 21:00-06:00 UTC (wraps)
        "sydney": {"start": 22, "end": 7},      # 22:00-07:00 UTC (wraps)
    }
    
    @staticmethod
    def get_utc_now() -> datetime:
        """
        Get current UTC time.
        
        Returns:
            Current UTC datetime
        """
        return datetime.now(pytz.UTC).replace(tzinfo=None)
    
    @staticmethod
    def is_trading_session_active(session_name: str, 
                                  utc_time: datetime = None) -> bool:
        """
        Check if a specific trading session is active.
        
        Args:
            session_name: Session name (london, newyork, tokyo, sydney)
            utc_time: UTC time to check (defaults to now)
            
        Returns:
            True if session is active
        """
        if utc_time is None:
            utc_time = TimeUtils.get_utc_now()
        
        session = TimeUtils.SESSIONS.get(session_name.lower())
        if not session:
            return False
        
        hour = utc_time.hour
        start = session["start"]
        end = session["end"]
        
        # Handle sessions that wrap midnight
        if start >= end:  # tokyo, sydney
            return hour >= start or hour < end
        else:
            return start <= hour < end
    
    @staticmethod
    def get_active_sessions(utc_time: datetime = None) -> list:
        """
        Get all currently active trading sessions.
        
        Args:
            utc_time: UTC time to check (defaults to now)
            
        Returns:
            List of active session names
        """
        if utc_time is None:
            utc_time = TimeUtils.get_utc_now()
        
        active = []
        for session_name in TimeUtils.SESSIONS.keys():
            if TimeUtils.is_trading_session_active(session_name, utc_time):
                active.append(session_name)
        
        return active
    
    @staticmethod
    def convert_to_timezone(utc_time: datetime, tz_name: str) -> datetime:
        """
        Convert UTC time to specified timezone.
        
        Args:
            utc_time: UTC datetime
            tz_name: Timezone name (e.g., 'US/Eastern', 'Europe/London')
            
        Returns:
            Converted datetime in specified timezone
        """
        tz = pytz.timezone(tz_name)
        utc_aware = pytz.UTC.localize(utc_time)
        return utc_aware.astimezone(tz)
    
    @staticmethod
    def is_weekend(utc_time: datetime = None) -> bool:
        """
        Check if current time is weekend.
        
        Note: Forex markets close Friday evening and reopen Sunday evening (UTC).
        
        Args:
            utc_time: UTC time to check (defaults to now)
            
        Returns:
            True if weekend
        """
        if utc_time is None:
            utc_time = TimeUtils.get_utc_now()
        
        # weekday() returns 0-6 (Monday-Sunday)
        weekday = utc_time.weekday()
        return weekday >= 5  # Saturday=5, Sunday=6
    
    @staticmethod
    def is_market_open(utc_time: datetime = None) -> bool:
        """
        Check if forex market is generally open.
        
        Forex trades 5 days a week, closes Friday afternoon UTC,
        reopens Sunday afternoon UTC.
        
        Args:
            utc_time: UTC time to check (defaults to now)
            
        Returns:
            True if market is open
        """
        if utc_time is None:
            utc_time = TimeUtils.get_utc_now()
        
        weekday = utc_time.weekday()  # 0=Monday, 6=Sunday
        
        if weekday < 4:  # Monday-Thursday: always open
            return True
        elif weekday == 4:  # Friday
            # Close at 22:00 UTC (Friday evening)
            return utc_time.hour < 22
        elif weekday == 5:  # Saturday: closed
            return False
        else:  # Sunday
            # Open from 22:00 UTC Sunday (21:00 Saturday in US)
            return utc_time.hour >= 22
    
    @staticmethod
    def time_until_next_session(session_name: str, 
                                utc_time: datetime = None) -> timedelta:
        """
        Calculate time until next session opens.
        
        Args:
            session_name: Session name
            utc_time: Current UTC time (defaults to now)
            
        Returns:
            Timedelta until session opens
        """
        if utc_time is None:
            utc_time = TimeUtils.get_utc_now()
        
        session = TimeUtils.SESSIONS.get(session_name.lower())
        if not session:
            return None
        
        hour = utc_time.hour
        start = session["start"]
        
        if TimeUtils.is_trading_session_active(session_name, utc_time):
            return timedelta(0)  # Already active
        
        # Calculate hours until session starts
        if start > hour:
            hours_until = start - hour
        else:
            hours_until = 24 - hour + start
        
        minutes_until = hours_until * 60 - utc_time.minute
        
        return timedelta(minutes=minutes_until)
    
    @staticmethod
    def format_time_duration(td: timedelta) -> str:
        """
        Format timedelta as readable string.
        
        Args:
            td: Timedelta object
            
        Returns:
            Formatted string (e.g., "2h 30m")
        """
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
