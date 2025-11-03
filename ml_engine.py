import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import asyncio
import json

class MLEngine:
    def __init__(self):
        self.usage_model = RandomForestRegressor(n_estimators=100)
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.behavior_clusterer = KMeans(n_clusters=5)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    async def process_usage(self, usage_data: dict):
        """Process incoming usage data and generate insights"""
        features = self._extract_features(usage_data)
        
        if not self.is_trained:
            await self._train_models()
        
        # Detect anomalies
        anomaly_score = self.anomaly_detector.decision_function([features])[0]
        is_anomaly = anomaly_score < -0.5
        
        # Predict next usage
        next_usage = self.usage_model.predict([features])[0]
        
        # Generate insights
        insights = {
            "predicted_next_usage": float(next_usage),
            "anomaly_detected": bool(is_anomaly),
            "anomaly_score": float(anomaly_score),
            "risk_level": self._calculate_risk_level(features),
            "recommendations": self._generate_quick_recommendations(features)
        }
        
        return insights
    
    def _extract_features(self, usage_data: dict):
        """Extract ML features from usage data"""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        
        return [
            usage_data.get("duration", 0),
            hour,
            day_of_week,
            usage_data.get("app_category", 0),
            usage_data.get("session_count", 1)
        ]
    
    async def _train_models(self):
        """Train ML models with synthetic data"""
        # Generate synthetic training data
        X, y = self._generate_training_data()
        
        # Train models
        self.usage_model.fit(X, y)
        self.anomaly_detector.fit(X)
        self.behavior_clusterer.fit(X)
        
        self.is_trained = True
    
    def _generate_training_data(self):
        """Generate synthetic training data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [duration, hour, day_of_week, app_category, session_count]
        X = np.random.rand(n_samples, 5)
        X[:, 0] *= 120  # duration in minutes
        X[:, 1] *= 24   # hour of day
        X[:, 2] *= 7    # day of week
        X[:, 3] *= 5    # app category
        X[:, 4] *= 10   # session count
        
        # Target: next usage duration
        y = X[:, 0] * 0.8 + np.random.normal(0, 10, n_samples)
        
        return X, y
    
    def _calculate_risk_level(self, features):
        """Calculate addiction risk level"""
        duration = features[0]
        hour = features[1]
        
        if duration > 60 and (hour < 8 or hour > 22):
            return "high"
        elif duration > 30:
            return "medium"
        else:
            return "low"
    
    def _generate_quick_recommendations(self, features):
        """Generate quick recommendations based on current usage"""
        duration = features[0]
        hour = features[1]
        
        recommendations = []
        
        if duration > 45:
            recommendations.append("Take a 10-minute break")
        
        if hour > 22:
            recommendations.append("Consider winding down for better sleep")
        
        if hour < 8:
            recommendations.append("Morning screen time affects your day")
        
        return recommendations
    
    async def generate_recommendations(self, user_id: str):
        """Generate personalized recommendations"""
        # Simulate user behavior analysis
        recommendations = [
            {
                "type": "break_reminder",
                "message": "Take a 5-minute break every 30 minutes",
                "priority": "high"
            },
            {
                "type": "app_limit",
                "message": "Consider limiting social media to 1 hour daily",
                "priority": "medium"
            },
            {
                "type": "alternative_activity",
                "message": "Try reading or outdoor activities instead",
                "priority": "low"
            }
        ]
        
        return recommendations
    
    async def optimize_break_timing(self, data: dict):
        """Optimize break timing based on usage patterns"""
        current_usage = data.get("current_usage", 0)
        daily_pattern = data.get("daily_pattern", [])
        
        # Simple optimization algorithm
        optimal_breaks = []
        
        if current_usage > 30:
            optimal_breaks.append({
                "time": datetime.now() + timedelta(minutes=5),
                "duration": 5,
                "type": "micro_break"
            })
        
        if current_usage > 60:
            optimal_breaks.append({
                "time": datetime.now() + timedelta(minutes=15),
                "duration": 15,
                "type": "active_break"
            })
        
        return optimal_breaks