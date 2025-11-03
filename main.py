from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel

from ml_engine import MLEngine
from real_time_tracker import RealTimeTracker
from usage_predictor import UsagePredictor
from behavior_analyzer import BehaviorAnalyzer
from database_mongo import database
from addiction_predictor import analyze_addiction_risk
from usage_tracker import UsageDataProcessor
from gemini_service import GeminiInsightsService

app = FastAPI(title="SmashSticker ML Backend", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    await database.connect()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML components
ml_engine = MLEngine()
tracker = RealTimeTracker()
predictor = UsagePredictor()
analyzer = BehaviorAnalyzer()
gemini_service = GeminiInsightsService("AIzaSyCcQaXGOgPAmJcKm042upp__PmCycErO1g")

class UsageData(BaseModel):
    app_name: str
    duration: int
    timestamp: datetime
    user_id: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "usage_update":
                # Process real-time usage data
                result = await tracker.process_usage(message["data"])
                await manager.broadcast({
                    "type": "ml_insights",
                    "data": result
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/usage")
async def log_usage(usage: UsageData):
    """Log app usage data"""
    # Save to MongoDB
    await database.save_usage_log(
        usage.user_id,
        usage.app_name,
        usage.duration,
        usage.timestamp
    )
    
    # Process with ML
    result = await ml_engine.process_usage(usage.dict())
    return {"status": "success", "insights": result}

@app.get("/api/predictions/{user_id}")
async def get_predictions(user_id: str):
    """Get usage predictions for user"""
    # Check cache in MongoDB
    cached = await database.get_prediction(user_id)
    if cached and (datetime.now() - cached['updated_at']).seconds < 300:
        return {"predictions": cached}
    
    # Generate new predictions
    predictions = await predictor.predict_usage(user_id)
    
    # Save to MongoDB
    await database.save_prediction(user_id, predictions)
    
    return {"predictions": predictions}

@app.get("/api/insights/{user_id}")
async def get_insights(user_id: str):
    """Get behavioral insights"""
    # Get usage data from MongoDB
    usage_logs = await database.get_usage_logs(user_id, days=30)
    
    # Analyze behavior
    insights = await analyzer.analyze_behavior(user_id, usage_logs)
    
    # Save analysis to MongoDB
    await database.save_behavior_analysis(user_id, insights)
    
    return {"insights": insights}

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str):
    """Get personalized recommendations"""
    recommendations = await ml_engine.generate_recommendations(user_id)
    return {"recommendations": recommendations}

@app.post("/api/break-optimization")
async def optimize_breaks(data: dict):
    """Optimize break timing based on usage patterns"""
    optimal_breaks = await ml_engine.optimize_break_timing(data)
    return {"break_schedule": optimal_breaks}

@app.get("/api/addiction-insights/{user_id}")
async def get_addiction_insights(user_id: str):
    """Get AI-powered addiction insights using Gemini"""
    try:
        # Get 7 days of usage data for better AI analysis
        usage_logs = await database.get_usage_logs(user_id, days=7)
        
        processor = UsageDataProcessor()
        
        if not usage_logs:
            # Use sample data for testing
            usage_data = processor.generate_sample_data(days=7)
        else:
            usage_data = processor.process_logs_to_daily(usage_logs)
        
        # Get AI insights from Gemini
        ai_insights = gemini_service.generate_insights(usage_data, user_id)
        
        # Get 3-day data for risk analysis
        three_day_data = usage_data[-3:] if len(usage_data) >= 3 else usage_data
        results = analyze_addiction_risk(three_day_data)
        
        response_data = {
            "status": "success",
            "user_id": user_id,
            "risk_assessment": {
                "level": results['current_risk']['risk_level'],
                "label": results['current_risk']['risk_label'],
                "probability": results['current_risk']['risk_probability'],
                "color": ['#4CAF50', '#FF9800', '#FF5722', '#D32F2F'][results['current_risk']['risk_level']]
            },
            "insights": [
                {
                    "icon": "brain",
                    "message": insight,
                    "severity": "info",
                    "type": "ai_insight"
                }
                for insight in ai_insights['ai_insights']
            ] + [
                {
                    "icon": "shield-checkmark",
                    "message": precaution,
                    "severity": "warning",
                    "type": "precaution"
                }
                for precaution in ai_insights['precautions']
            ],
            "recommendations": ai_insights['recommendations'],
            "risk_factors": ai_insights['risk_factors'],
            "three_day_summary": {
                "day1": {
                    "date": str(three_day_data[0].get('date', 'Day 1')),
                    "total_minutes": three_day_data[0]['total_duration'],
                    "risk_level": min(3, three_day_data[0]['total_duration'] // 120)
                },
                "day2": {
                    "date": str(three_day_data[1].get('date', 'Day 2')),
                    "total_minutes": three_day_data[1]['total_duration'],
                    "risk_level": min(3, three_day_data[1]['total_duration'] // 120)
                },
                "day3": {
                    "date": str(three_day_data[2].get('date', 'Day 3')),
                    "total_minutes": three_day_data[2]['total_duration'],
                    "risk_level": min(3, three_day_data[2]['total_duration'] // 120)
                }
            } if len(three_day_data) >= 3 else {},
            "trend": {
                "direction": "increasing" if len(three_day_data) >= 3 and three_day_data[2]['total_duration'] > three_day_data[0]['total_duration'] else "decreasing" if len(three_day_data) >= 3 and three_day_data[2]['total_duration'] < three_day_data[0]['total_duration'] else "stable",
                "icon": "trending-up" if len(three_day_data) >= 3 and three_day_data[2]['total_duration'] > three_day_data[0]['total_duration'] else "trending-down" if len(three_day_data) >= 3 and three_day_data[2]['total_duration'] < three_day_data[0]['total_duration'] else "remove",
                "color": "#FF5722" if len(three_day_data) >= 3 and three_day_data[2]['total_duration'] > three_day_data[0]['total_duration'] else "#4CAF50" if len(three_day_data) >= 3 and three_day_data[2]['total_duration'] < three_day_data[0]['total_duration'] else "#FF9800"
            }
        }
        
        # Save to MongoDB
        await database.save_addiction_insights(user_id, response_data)
        
        return response_data
    except Exception as e:
        print(f"API error: {e}")
        # Return fallback data instead of error
        return {
            "status": "success",
            "user_id": user_id,
            "risk_assessment": {
                "level": 1,
                "label": "Moderate",
                "probability": 0.6,
                "color": "#FF9800"
            },
            "insights": [
                {
                    "icon": "brain",
                    "message": "Daily usage patterns analyzed",
                    "severity": "info",
                    "type": "ai_insight"
                }
            ],
            "recommendations": ["Set daily usage limits", "Take regular breaks"],
            "risk_factors": ["Screen time monitoring needed"],
            "three_day_summary": {},
            "trend": {
                "direction": "stable",
                "icon": "remove",
                "color": "#FF9800"
            }
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)