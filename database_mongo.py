"""
MongoDB database implementation for addiction tracker
"""
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv('MONGO_DB', 'mongodb://localhost:27017')

class MongoDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=2000)
            self.db = self.client.addiction_tracker
            await self.client.admin.command('ping')
            print("Connected to MongoDB")
        except Exception as e:
            print(f"MongoDB connection failed: {e}. Using fallback mode.")
            self.client = None
            self.db = None
    
    async def save_usage_log(self, user_id: str, app_name: str, duration: int, timestamp: datetime):
        """Save usage log to MongoDB"""
        if not self.db:
            return
        try:
            await self.db.usage_logs.insert_one({
                'user_id': user_id,
                'app_name': app_name,
                'duration': duration,
                'timestamp': timestamp,
                'created_at': datetime.now()
            })
        except:
            pass
    
    async def get_usage_logs(self, user_id: str, days: int = 30) -> List[dict]:
        """Get usage logs from MongoDB"""
        if not self.db:
            return []
        try:
            start_date = datetime.now() - timedelta(days=days)
            cursor = self.db.usage_logs.find({
                'user_id': user_id,
                'timestamp': {'$gte': start_date}
            }).sort('timestamp', -1)
            return await cursor.to_list(length=None)
        except:
            return []
    
    async def save_prediction(self, user_id: str, predictions: dict):
        """Save ML predictions to MongoDB"""
        await self.db.predictions.update_one(
            {'user_id': user_id},
            {'$set': {**predictions, 'updated_at': datetime.now()}},
            upsert=True
        )
    
    async def get_prediction(self, user_id: str) -> Optional[dict]:
        """Get latest predictions from MongoDB"""
        return await self.db.predictions.find_one({'user_id': user_id})
    
    async def save_behavior_analysis(self, user_id: str, analysis: dict):
        """Save behavior analysis to MongoDB"""
        await self.db.behavior_analysis.insert_one({
            'user_id': user_id,
            **analysis,
            'created_at': datetime.now()
        })
    
    async def get_latest_behavior_analysis(self, user_id: str) -> Optional[dict]:
        """Get latest behavior analysis from MongoDB"""
        return await self.db.behavior_analysis.find_one(
            {'user_id': user_id},
            sort=[('created_at', -1)]
        )
    
    async def save_addiction_insights(self, user_id: str, insights: dict):
        """Save addiction insights to MongoDB"""
        await self.db.addiction_insights.insert_one({
            'user_id': user_id,
            **insights,
            'created_at': datetime.now()
        })
    
    async def get_latest_addiction_insights(self, user_id: str) -> Optional[dict]:
        """Get latest addiction insights from MongoDB"""
        return await self.db.addiction_insights.find_one(
            {'user_id': user_id},
            sort=[('created_at', -1)]
        )
    
    async def save_user(self, user_id: str, data: dict):
        """Save user data to MongoDB"""
        await self.db.users.update_one(
            {'user_id': user_id},
            {'$set': {**data, 'updated_at': datetime.now()}},
            upsert=True
        )
    
    async def get_user(self, user_id: str) -> Optional[dict]:
        """Get user data from MongoDB"""
        return await self.db.users.find_one({'user_id': user_id})
    
    async def get_user_stats(self, user_id: str) -> dict:
        """Get aggregated user statistics from MongoDB"""
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$group': {
                '_id': '$user_id',
                'total_usage': {'$sum': '$duration'},
                'session_count': {'$sum': 1},
                'avg_session': {'$avg': '$duration'}
            }}
        ]
        result = await self.db.usage_logs.aggregate(pipeline).to_list(1)
        return result[0] if result else {}

database = MongoDatabase()
