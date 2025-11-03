"""
Seed sample data for testing
Run: python seed_data.py
"""
import asyncio
from datetime import datetime, timedelta
import random
from database_mongo import database

async def seed_data():
    print("🌱 Seeding sample data...")
    
    await database.connect()
    
    user_id = "default_user"
    
    # Generate 3 days of usage data
    for day_offset in range(3):
        date = datetime.now() - timedelta(days=2-day_offset)
        
        # Generate 10-20 sessions per day
        sessions = random.randint(10, 20)
        
        for _ in range(sessions):
            timestamp = date.replace(
                hour=random.randint(6, 23),
                minute=random.randint(0, 59),
                second=0
            )
            
            app_name = random.choice([
                'Instagram', 'TikTok', 'YouTube', 'WhatsApp',
                'Chrome', 'Games', 'Netflix', 'Spotify'
            ])
            
            duration = int(random.expovariate(1/15) + 5)  # 5-60 minutes
            
            await database.save_usage_log(user_id, app_name, duration, timestamp)
    
    print(f"✅ Seeded data for user: {user_id}")
    print("✅ 3 days of usage logs created")
    print("\nNow start the server: python start_server.py")

if __name__ == "__main__":
    asyncio.run(seed_data())
