import asyncio
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

class RealTimeTracker:
    def __init__(self):
        self.active_sessions = {}
        self.usage_buffer = deque(maxlen=1000)
        self.pattern_detector = PatternDetector()
        self.alert_system = AlertSystem()
        
    async def process_usage(self, usage_data: dict):
        """Process real-time usage data"""
        user_id = usage_data.get("user_id", "default")
        app_name = usage_data.get("app_name", "unknown")
        timestamp = datetime.now()
        
        # Update active session
        session_key = f"{user_id}_{app_name}"
        if session_key not in self.active_sessions:
            self.active_sessions[session_key] = {
                "start_time": timestamp,
                "total_time": 0,
                "interactions": 0
            }
        
        session = self.active_sessions[session_key]
        session["interactions"] += 1
        session["total_time"] = (timestamp - session["start_time"]).total_seconds()
        
        # Add to buffer for pattern analysis
        self.usage_buffer.append({
            "user_id": user_id,
            "app_name": app_name,
            "timestamp": timestamp,
            "session_duration": session["total_time"],
            "interactions": session["interactions"]
        })
        
        # Detect patterns
        patterns = await self.pattern_detector.detect_patterns(list(self.usage_buffer))
        
        # Check for alerts
        alerts = await self.alert_system.check_alerts(session, patterns)
        
        return {
            "session_info": session,
            "patterns": patterns,
            "alerts": alerts,
            "real_time_metrics": self._calculate_real_time_metrics(user_id)
        }
    
    def _calculate_real_time_metrics(self, user_id: str):
        """Calculate real-time usage metrics"""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Filter today's data
        today_usage = [
            entry for entry in self.usage_buffer
            if entry["user_id"] == user_id and entry["timestamp"] >= today_start
        ]
        
        if not today_usage:
            return {"total_time": 0, "app_count": 0, "avg_session": 0}
        
        total_time = sum(entry["session_duration"] for entry in today_usage)
        unique_apps = len(set(entry["app_name"] for entry in today_usage))
        avg_session = total_time / len(today_usage) if today_usage else 0
        
        return {
            "total_time": total_time / 60,  # Convert to minutes
            "app_count": unique_apps,
            "avg_session": avg_session / 60,  # Convert to minutes
            "current_streak": self._calculate_current_streak(today_usage)
        }
    
    def _calculate_current_streak(self, usage_data):
        """Calculate current usage streak"""
        if not usage_data:
            return 0
        
        # Sort by timestamp
        sorted_usage = sorted(usage_data, key=lambda x: x["timestamp"])
        
        # Calculate streak (continuous usage within 5-minute gaps)
        streak = 0
        last_time = None
        
        for entry in sorted_usage:
            if last_time is None:
                streak = entry["session_duration"]
            else:
                gap = (entry["timestamp"] - last_time).total_seconds()
                if gap <= 300:  # 5 minutes
                    streak += entry["session_duration"]
                else:
                    streak = entry["session_duration"]
            
            last_time = entry["timestamp"]
        
        return streak / 60  # Convert to minutes

class PatternDetector:
    def __init__(self):
        self.pattern_cache = {}
        
    async def detect_patterns(self, usage_data):
        """Detect usage patterns in real-time"""
        if len(usage_data) < 10:
            return {"patterns": [], "confidence": 0}
        
        patterns = []
        
        # Detect binge usage pattern
        binge_pattern = self._detect_binge_pattern(usage_data)
        if binge_pattern:
            patterns.append(binge_pattern)
        
        # Detect time-based patterns
        time_pattern = self._detect_time_patterns(usage_data)
        if time_pattern:
            patterns.append(time_pattern)
        
        # Detect app switching pattern
        switching_pattern = self._detect_app_switching(usage_data)
        if switching_pattern:
            patterns.append(switching_pattern)
        
        return {
            "patterns": patterns,
            "confidence": self._calculate_pattern_confidence(patterns)
        }
    
    def _detect_binge_pattern(self, usage_data):
        """Detect binge usage patterns"""
        recent_data = usage_data[-20:]  # Last 20 entries
        
        if len(recent_data) < 5:
            return None
        
        # Check for continuous usage over 1 hour
        total_time = sum(entry["session_duration"] for entry in recent_data)
        
        if total_time > 3600:  # 1 hour
            return {
                "type": "binge_usage",
                "severity": "high" if total_time > 7200 else "medium",
                "duration": total_time / 60,
                "recommendation": "Take a longer break"
            }
        
        return None
    
    def _detect_time_patterns(self, usage_data):
        """Detect time-based usage patterns"""
        hour_usage = defaultdict(float)
        
        for entry in usage_data:
            hour = entry["timestamp"].hour
            hour_usage[hour] += entry["session_duration"]
        
        # Find peak usage hours
        if hour_usage:
            peak_hour = max(hour_usage, key=hour_usage.get)
            peak_usage = hour_usage[peak_hour] / 60  # Convert to minutes
            
            if peak_usage > 60:  # More than 1 hour in a single hour
                return {
                    "type": "peak_usage_time",
                    "peak_hour": peak_hour,
                    "peak_usage": peak_usage,
                    "recommendation": f"Consider limiting usage during {peak_hour}:00"
                }
        
        return None
    
    def _detect_app_switching(self, usage_data):
        """Detect rapid app switching behavior"""
        recent_data = usage_data[-10:]  # Last 10 entries
        
        if len(recent_data) < 5:
            return None
        
        # Count unique apps in recent usage
        unique_apps = len(set(entry["app_name"] for entry in recent_data))
        
        if unique_apps >= 5:  # Switching between 5+ apps recently
            return {
                "type": "app_switching",
                "app_count": unique_apps,
                "recommendation": "Focus on one app at a time"
            }
        
        return None
    
    def _calculate_pattern_confidence(self, patterns):
        """Calculate confidence score for detected patterns"""
        if not patterns:
            return 0
        
        # Simple confidence calculation based on pattern count and severity
        confidence = min(len(patterns) * 0.3, 1.0)
        
        for pattern in patterns:
            if pattern.get("severity") == "high":
                confidence += 0.2
            elif pattern.get("severity") == "medium":
                confidence += 0.1
        
        return min(confidence, 1.0)

class AlertSystem:
    def __init__(self):
        self.alert_thresholds = {
            "session_duration": 1800,  # 30 minutes
            "daily_limit": 7200,       # 2 hours
            "late_night_usage": 22,    # 10 PM
            "early_morning_usage": 6   # 6 AM
        }
        
    async def check_alerts(self, session_info, patterns):
        """Check for usage alerts"""
        alerts = []
        
        # Session duration alert
        if session_info["total_time"] > self.alert_thresholds["session_duration"]:
            alerts.append({
                "type": "long_session",
                "message": "You've been using this app for over 30 minutes",
                "action": "take_break",
                "priority": "medium"
            })
        
        # Pattern-based alerts
        for pattern in patterns.get("patterns", []):
            if pattern["type"] == "binge_usage":
                alerts.append({
                    "type": "binge_detected",
                    "message": f"Binge usage detected: {pattern['duration']:.1f} minutes",
                    "action": "limit_usage",
                    "priority": "high"
                })
        
        # Time-based alerts
        current_hour = datetime.now().hour
        if current_hour >= self.alert_thresholds["late_night_usage"]:
            alerts.append({
                "type": "late_night_usage",
                "message": "Late night usage may affect your sleep",
                "action": "wind_down",
                "priority": "medium"
            })
        
        return alerts