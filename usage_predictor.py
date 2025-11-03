import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import asyncio
import json

class UsagePredictor:
    def __init__(self):
        self.hourly_model = RandomForestRegressor(n_estimators=50)
        self.daily_model = GradientBoostingRegressor(n_estimators=50)
        self.app_model = RandomForestRegressor(n_estimators=30)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_history = []
        
    async def predict_usage(self, user_id: str):
        """Predict future usage patterns"""
        if not self.is_trained:
            await self._train_models()
        
        current_features = self._get_current_features()
        
        # Predict next hour usage
        next_hour_usage = self.hourly_model.predict([current_features])[0]
        
        # Predict daily total
        daily_features = self._get_daily_features()
        daily_total = self.daily_model.predict([daily_features])[0]
        
        # Predict app-specific usage
        app_predictions = await self._predict_app_usage(current_features)
        
        # Calculate break recommendations
        break_recommendations = self._calculate_break_timing(next_hour_usage)
        
        return {
            "next_hour_usage": max(0, float(next_hour_usage)),
            "daily_total_prediction": max(0, float(daily_total)),
            "app_predictions": app_predictions,
            "break_recommendations": break_recommendations,
            "confidence_score": self._calculate_confidence(),
            "risk_assessment": self._assess_risk(next_hour_usage, daily_total)
        }
    
    def _get_current_features(self):
        """Extract current time-based features"""
        now = datetime.now()
        
        return [
            now.hour,                    # Hour of day (0-23)
            now.weekday(),              # Day of week (0-6)
            now.day,                    # Day of month
            (now - datetime(now.year, 1, 1)).days,  # Day of year
            1 if now.weekday() >= 5 else 0,  # Is weekend
            self._get_recent_usage(),   # Recent usage trend
            self._get_session_count(),  # Current session count
        ]
    
    def _get_daily_features(self):
        """Extract daily pattern features"""
        now = datetime.now()
        
        return [
            now.weekday(),              # Day of week
            now.hour,                   # Current hour
            self._get_daily_usage_so_far(),  # Usage so far today
            self._get_weekly_average(), # Weekly average
            1 if self._is_holiday() else 0,  # Is holiday
        ]
    
    def _get_recent_usage(self):
        """Get recent usage trend (last 2 hours)"""
        # Simulate recent usage data
        return np.random.uniform(10, 60)  # Minutes in last 2 hours
    
    def _get_session_count(self):
        """Get current session count for today"""
        return np.random.randint(1, 20)  # Number of app sessions today
    
    def _get_daily_usage_so_far(self):
        """Get usage accumulated so far today"""
        current_hour = datetime.now().hour
        # Simulate progressive usage throughout the day
        return current_hour * np.random.uniform(5, 15)
    
    def _get_weekly_average(self):
        """Get weekly usage average"""
        return np.random.uniform(120, 300)  # Minutes per day average
    
    def _is_holiday(self):
        """Check if current day is a holiday"""
        # Simple holiday detection (can be enhanced)
        now = datetime.now()
        return now.weekday() >= 5  # Weekend as holiday
    
    async def _train_models(self):
        """Train prediction models with synthetic data"""
        # Generate synthetic training data
        X_hourly, y_hourly = self._generate_hourly_data()
        X_daily, y_daily = self._generate_daily_data()
        
        # Train models
        self.hourly_model.fit(X_hourly, y_hourly)
        self.daily_model.fit(X_daily, y_daily)
        
        # Train app-specific model
        X_app, y_app = self._generate_app_data()
        self.app_model.fit(X_app, y_app)
        
        self.is_trained = True
    
    def _generate_hourly_data(self):
        """Generate synthetic hourly usage data"""
        np.random.seed(42)
        n_samples = 1000
        
        # Features: [hour, weekday, day, day_of_year, is_weekend, recent_usage, session_count]
        X = np.random.rand(n_samples, 7)
        X[:, 0] *= 24  # hour
        X[:, 1] *= 7   # weekday
        X[:, 2] *= 31  # day
        X[:, 3] *= 365 # day_of_year
        X[:, 4] = np.random.choice([0, 1], n_samples)  # is_weekend
        X[:, 5] *= 120 # recent_usage
        X[:, 6] *= 20  # session_count
        
        # Target: next hour usage (influenced by time patterns)
        y = (
            np.sin(X[:, 0] / 24 * 2 * np.pi) * 30 +  # Daily pattern
            X[:, 4] * 20 +  # Weekend effect
            X[:, 5] * 0.3 +  # Recent usage influence
            np.random.normal(0, 10, n_samples)  # Noise
        )
        y = np.maximum(y, 0)  # Ensure non-negative
        
        return X, y
    
    def _generate_daily_data(self):
        """Generate synthetic daily usage data"""
        np.random.seed(43)
        n_samples = 500
        
        # Features: [weekday, hour, usage_so_far, weekly_avg, is_holiday]
        X = np.random.rand(n_samples, 5)
        X[:, 0] *= 7   # weekday
        X[:, 1] *= 24  # hour
        X[:, 2] *= 300 # usage_so_far
        X[:, 3] *= 400 # weekly_avg
        X[:, 4] = np.random.choice([0, 1], n_samples)  # is_holiday
        
        # Target: daily total usage
        y = (
            X[:, 3] +  # Base weekly average
            X[:, 4] * 50 +  # Holiday effect
            (7 - X[:, 0]) * 10 +  # Weekday effect
            np.random.normal(0, 30, n_samples)  # Noise
        )
        y = np.maximum(y, 0)
        
        return X, y
    
    def _generate_app_data(self):
        """Generate synthetic app-specific usage data"""
        np.random.seed(44)
        n_samples = 800
        
        # Features: [hour, weekday, app_category, recent_app_usage]
        X = np.random.rand(n_samples, 4)
        X[:, 0] *= 24  # hour
        X[:, 1] *= 7   # weekday
        X[:, 2] *= 5   # app_category (0-4)
        X[:, 3] *= 60  # recent_app_usage
        
        # Target: app usage duration
        y = (
            X[:, 2] * 15 +  # Category influence
            np.sin(X[:, 0] / 24 * 2 * np.pi) * 20 +  # Time pattern
            X[:, 3] * 0.5 +  # Recent usage influence
            np.random.normal(0, 8, n_samples)
        )
        y = np.maximum(y, 0)
        
        return X, y
    
    async def _predict_app_usage(self, current_features):
        """Predict usage for specific app categories"""
        app_categories = ["Social", "Games", "Productivity", "Entertainment", "Education"]
        predictions = {}
        
        for i, category in enumerate(app_categories):
            # Create app-specific features
            app_features = [
                current_features[0],  # hour
                current_features[1],  # weekday
                i,                    # app_category
                np.random.uniform(0, 30)  # recent_app_usage
            ]
            
            predicted_usage = self.app_model.predict([app_features])[0]
            predictions[category] = max(0, float(predicted_usage))
        
        return predictions
    
    def _calculate_break_timing(self, predicted_usage):
        """Calculate optimal break timing"""
        breaks = []
        
        if predicted_usage > 30:
            # Suggest micro-breaks every 20 minutes
            for i in range(0, int(predicted_usage), 20):
                breaks.append({
                    "time_offset": i,
                    "duration": 2,
                    "type": "micro_break",
                    "activity": "Look away from screen"
                })
        
        if predicted_usage > 60:
            # Suggest longer break after 45 minutes
            breaks.append({
                "time_offset": 45,
                "duration": 10,
                "type": "active_break",
                "activity": "Stand up and stretch"
            })
        
        return breaks
    
    def _calculate_confidence(self):
        """Calculate prediction confidence score"""
        # Simple confidence based on model training and data availability
        base_confidence = 0.7 if self.is_trained else 0.3
        
        # Adjust based on time of day (more confident during regular hours)
        current_hour = datetime.now().hour
        if 8 <= current_hour <= 22:
            time_confidence = 0.9
        else:
            time_confidence = 0.6
        
        return base_confidence * time_confidence
    
    def _assess_risk(self, next_hour_usage, daily_total):
        """Assess addiction risk based on predictions"""
        risk_factors = []
        risk_score = 0
        
        if next_hour_usage > 45:
            risk_factors.append("High predicted usage next hour")
            risk_score += 0.3
        
        if daily_total > 240:  # 4 hours
            risk_factors.append("High daily usage predicted")
            risk_score += 0.4
        
        current_hour = datetime.now().hour
        if current_hour > 22 and next_hour_usage > 20:
            risk_factors.append("Late night usage predicted")
            risk_score += 0.3
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendations": self._get_risk_recommendations(risk_level)
        }
    
    def _get_risk_recommendations(self, risk_level):
        """Get recommendations based on risk level"""
        recommendations = {
            "high": [
                "Set strict app limits immediately",
                "Take a 30-minute break now",
                "Consider digital detox activities"
            ],
            "medium": [
                "Monitor usage closely",
                "Set break reminders",
                "Plan alternative activities"
            ],
            "low": [
                "Continue current habits",
                "Maintain awareness",
                "Keep up the good work"
            ]
        }
        
        return recommendations.get(risk_level, [])