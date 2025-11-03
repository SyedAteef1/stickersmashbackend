from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import os

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['smasher_db']

# Collections
users_collection = db['users']
usage_logs_collection = db['usage_logs']
predictions_collection = db['predictions']
behavior_analysis_collection = db['behavior_analysis']

class Database:
    @staticmethod
    async def save_user(user_id: str, data: dict):
        """Save or update user data"""
        users_collection.update_one(
            {'user_id': user_id},
            {'$set': {**data, 'updated_at': datetime.now()}},
            upsert=True
        )
    
    @staticmethod
    async def get_user(user_id: str) -> Optional[dict]:
        """Get user data"""
        return users_collection.find_one({'user_id': user_id})
    
    @staticmethod
    async def save_usage_log(user_id: str, app_name: str, duration: int, timestamp: datetime):
        """Save usage log"""
        usage_logs_collection.insert_one({
            'user_id': user_id,
            'app_name': app_name,
            'duration': duration,
            'timestamp': timestamp,
            'created_at': datetime.now()
        })
    
    @staticmethod
    async def get_usage_logs(user_id: str, days: int = 30) -> List[dict]:
        """Get usage logs for user"""
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        cursor = usage_logs_collection.find({
            'user_id': user_id,
            'timestamp': {'$gte': start_date}
        }).sort('timestamp', -1)
        
        return list(cursor)
    
    @staticmethod
    async def save_prediction(user_id: str, predictions: dict):
        """Save ML predictions"""
        predictions_collection.update_one(
            {'user_id': user_id},
            {'$set': {**predictions, 'updated_at': datetime.now()}},
            upsert=True
        )
    
    @staticmethod
    async def get_prediction(user_id: str) -> Optional[dict]:
        """Get latest predictions"""
        return predictions_collection.find_one({'user_id': user_id})
    
    @staticmethod
    async def save_behavior_analysis(user_id: str, analysis: dict):
        """Save behavior analysis"""
        behavior_analysis_collection.insert_one({
            'user_id': user_id,
            **analysis,
            'created_at': datetime.now()
        })
    
    @staticmethod
    async def get_latest_behavior_analysis(user_id: str) -> Optional[dict]:
        """Get latest behavior analysis"""
        return behavior_analysis_collection.find_one(
            {'user_id': user_id},
            sort=[('created_at', -1)]
        )
    
    @staticmethod
    async def get_user_stats(user_id: str) -> dict:
        """Get aggregated user statistics"""
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': '$user_id',
                'total_usage': {'$sum': '$duration'},
                'session_count': {'$count': {}},
                'avg_session': {'$avg': '$duration'}
            }}
        ]
        
        result = list(usage_logs_collection.aggregate(pipeline))
        return result[0] if result else {}

database = Database()
