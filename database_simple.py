"""
Simple in-memory database for demo purposes
No MongoDB required!
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional

# In-memory storage
_storage = {
    'users': {},
    'usage_logs': {},
    'predictions': {},
    'behavior_analysis': {}
}

class Database:
    @staticmethod
    async def save_user(user_id: str, data: dict):
        """Save or update user data"""
        if user_id not in _storage['users']:
            _storage['users'][user_id] = {}
        _storage['users'][user_id].update({**data, 'updated_at': datetime.now()})
    
    @staticmethod
    async def get_user(user_id: str) -> Optional[dict]:
        """Get user data"""
        return _storage['users'].get(user_id)
    
    @staticmethod
    async def save_usage_log(user_id: str, app_name: str, duration: int, timestamp: datetime):
        """Save usage log"""
        if user_id not in _storage['usage_logs']:
            _storage['usage_logs'][user_id] = []
        
        _storage['usage_logs'][user_id].append({
            'user_id': user_id,
            'app_name': app_name,
            'duration': duration,
            'timestamp': timestamp,
            'created_at': datetime.now()
        })
    
    @staticmethod
    async def get_usage_logs(user_id: str, days: int = 30) -> List[dict]:
        """Get usage logs for user"""
        if user_id not in _storage['usage_logs']:
            return []
        
        start_date = datetime.now() - timedelta(days=days)
        logs = _storage['usage_logs'].get(user_id, [])
        
        # Filter by date and sort
        filtered = [log for log in logs if log['timestamp'] >= start_date]
        return sorted(filtered, key=lambda x: x['timestamp'], reverse=True)
    
    @staticmethod
    async def save_prediction(user_id: str, predictions: dict):
        """Save ML predictions"""
        if user_id not in _storage['predictions']:
            _storage['predictions'][user_id] = {}
        _storage['predictions'][user_id] = {**predictions, 'updated_at': datetime.now()}
    
    @staticmethod
    async def get_prediction(user_id: str) -> Optional[dict]:
        """Get latest predictions"""
        return _storage['predictions'].get(user_id)
    
    @staticmethod
    async def save_behavior_analysis(user_id: str, analysis: dict):
        """Save behavior analysis"""
        if user_id not in _storage['behavior_analysis']:
            _storage['behavior_analysis'][user_id] = []
        
        _storage['behavior_analysis'][user_id].append({
            'user_id': user_id,
            **analysis,
            'created_at': datetime.now()
        })
    
    @staticmethod
    async def get_latest_behavior_analysis(user_id: str) -> Optional[dict]:
        """Get latest behavior analysis"""
        analyses = _storage['behavior_analysis'].get(user_id, [])
        if not analyses:
            return None
        return max(analyses, key=lambda x: x['created_at'])
    
    @staticmethod
    async def get_user_stats(user_id: str) -> dict:
        """Get aggregated user statistics"""
        logs = _storage['usage_logs'].get(user_id, [])
        
        if not logs:
            return {}
        
        total_usage = sum(log['duration'] for log in logs)
        session_count = len(logs)
        avg_session = total_usage / session_count if session_count > 0 else 0
        
        return {
            'user_id': user_id,
            'total_usage': total_usage,
            'session_count': session_count,
            'avg_session': avg_session
        }

database = Database()

