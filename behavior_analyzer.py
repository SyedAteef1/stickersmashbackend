import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, Counter

class BehaviorAnalyzer:
    def __init__(self):
        self.behavior_clusterer = KMeans(n_clusters=4)
        self.anomaly_detector = DBSCAN(eps=0.5, min_samples=5)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=3)
        self.user_profiles = {}
        self.behavior_patterns = {}
        
    async def analyze_behavior(self, user_id: str, usage_logs: list = None):
        """Analyze user behavior patterns"""
        # Get user behavior data from MongoDB or use provided logs
        if usage_logs:
            behavior_data = self._convert_logs_to_behavior_data(usage_logs)
        else:
            behavior_data = await self._get_user_behavior_data(user_id)
        
        if not behavior_data:
            return {"message": "Insufficient data for analysis"}
        
        # Extract behavioral features
        features = self._extract_behavioral_features(behavior_data)
        
        # Perform clustering analysis
        cluster_analysis = await self._perform_clustering(features)
        
        # Detect behavioral anomalies
        anomalies = await self._detect_behavioral_anomalies(features)
        
        # Analyze usage patterns
        pattern_analysis = await self._analyze_usage_patterns(behavior_data)
        
        # Generate behavioral insights
        insights = await self._generate_behavioral_insights(
            cluster_analysis, anomalies, pattern_analysis
        )
        
        # Update user profile
        await self._update_user_profile(user_id, features, insights)
        
        return {
            "user_id": user_id,
            "behavior_cluster": cluster_analysis,
            "anomalies": anomalies,
            "patterns": pattern_analysis,
            "insights": insights,
            "recommendations": await self._generate_behavioral_recommendations(insights)
        }
    
    async def _get_user_behavior_data(self, user_id: str):
        """Simulate getting user behavior data"""
        # In real implementation, this would fetch from database
        np.random.seed(hash(user_id) % 1000)
        
        # Generate synthetic behavior data for the last 30 days
        data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for day in range(30):
            current_date = base_date + timedelta(days=day)
            
            # Simulate daily usage patterns
            daily_sessions = np.random.randint(5, 25)
            
            for session in range(daily_sessions):
                session_start = current_date + timedelta(
                    hours=np.random.uniform(6, 23),
                    minutes=np.random.uniform(0, 59)
                )
                
                data.append({
                    "timestamp": session_start,
                    "app_name": np.random.choice([
                        "Instagram", "TikTok", "YouTube", "WhatsApp", 
                        "Chrome", "Games", "Netflix", "Spotify"
                    ]),
                    "duration": np.random.exponential(15) + 1,  # Minutes
                    "interactions": np.random.poisson(10) + 1,
                    "day_of_week": session_start.weekday(),
                    "hour": session_start.hour
                })
        
        return data
    
    def _convert_logs_to_behavior_data(self, usage_logs: list):
        """Convert MongoDB usage logs to behavior data format"""
        data = []
        for log in usage_logs:
            timestamp = log.get('timestamp', datetime.now())
            data.append({
                "timestamp": timestamp,
                "app_name": log.get('app_name', 'Unknown'),
                "duration": log.get('duration', 0),
                "interactions": log.get('interactions', 1),
                "day_of_week": timestamp.weekday(),
                "hour": timestamp.hour
            })
        return data
    
    def _extract_behavioral_features(self, behavior_data):
        """Extract behavioral features for analysis"""
        if not behavior_data:
            return []
        
        # Group data by day
        daily_data = defaultdict(list)
        for entry in behavior_data:
            day_key = entry["timestamp"].date()
            daily_data[day_key].append(entry)
        
        features = []
        
        for day, sessions in daily_data.items():
            # Calculate daily behavioral metrics
            total_duration = sum(s["duration"] for s in sessions)
            total_interactions = sum(s["interactions"] for s in sessions)
            session_count = len(sessions)
            unique_apps = len(set(s["app_name"] for s in sessions))
            
            # Time-based features
            hours_used = set(s["hour"] for s in sessions)
            morning_usage = sum(1 for s in sessions if 6 <= s["hour"] < 12)
            afternoon_usage = sum(1 for s in sessions if 12 <= s["hour"] < 18)
            evening_usage = sum(1 for s in sessions if 18 <= s["hour"] < 22)
            night_usage = sum(1 for s in sessions if s["hour"] >= 22 or s["hour"] < 6)
            
            # App category distribution
            social_apps = ["Instagram", "TikTok", "WhatsApp"]
            entertainment_apps = ["YouTube", "Netflix", "Spotify", "Games"]
            
            social_time = sum(s["duration"] for s in sessions if s["app_name"] in social_apps)
            entertainment_time = sum(s["duration"] for s in sessions if s["app_name"] in entertainment_apps)
            
            # Behavioral patterns
            avg_session_duration = total_duration / session_count if session_count > 0 else 0
            interaction_rate = total_interactions / total_duration if total_duration > 0 else 0
            
            # Binge usage detection
            long_sessions = sum(1 for s in sessions if s["duration"] > 30)
            binge_score = long_sessions / session_count if session_count > 0 else 0
            
            features.append([
                total_duration,           # Total daily usage
                session_count,           # Number of sessions
                unique_apps,             # App diversity
                avg_session_duration,    # Average session length
                interaction_rate,        # Interactions per minute
                morning_usage,           # Morning sessions
                afternoon_usage,         # Afternoon sessions
                evening_usage,           # Evening sessions
                night_usage,             # Night sessions
                social_time,             # Social media time
                entertainment_time,      # Entertainment time
                binge_score,             # Binge usage indicator
                len(hours_used),         # Time spread
                day.weekday()            # Day of week
            ])
        
        return np.array(features)
    
    async def _perform_clustering(self, features):
        """Perform behavioral clustering analysis"""
        if len(features) < 4:
            return {"cluster": -1, "cluster_name": "Insufficient data"}
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features)
        
        # Perform clustering
        clusters = self.behavior_clusterer.fit_predict(features_scaled)
        
        # Analyze cluster characteristics
        cluster_centers = self.behavior_clusterer.cluster_centers_
        user_cluster = clusters[-1]  # Most recent behavior
        
        # Define cluster names based on characteristics
        cluster_names = {
            0: "Light User",
            1: "Heavy User", 
            2: "Binge User",
            3: "Balanced User"
        }
        
        # Calculate cluster statistics
        cluster_stats = self._calculate_cluster_stats(features, clusters, user_cluster)
        
        return {
            "cluster": int(user_cluster),
            "cluster_name": cluster_names.get(user_cluster, "Unknown"),
            "cluster_stats": cluster_stats,
            "stability": self._calculate_cluster_stability(clusters)
        }
    
    def _calculate_cluster_stats(self, features, clusters, user_cluster):
        """Calculate statistics for user's cluster"""
        cluster_data = features[clusters == user_cluster]
        
        if len(cluster_data) == 0:
            return {}
        
        return {
            "avg_daily_usage": float(np.mean(cluster_data[:, 0])),
            "avg_sessions": float(np.mean(cluster_data[:, 1])),
            "avg_app_diversity": float(np.mean(cluster_data[:, 2])),
            "avg_session_length": float(np.mean(cluster_data[:, 3])),
            "binge_tendency": float(np.mean(cluster_data[:, 11]))
        }
    
    def _calculate_cluster_stability(self, clusters):
        """Calculate how stable the user's cluster assignment is"""
        if len(clusters) < 7:
            return 0.5
        
        # Check consistency of recent clusters
        recent_clusters = clusters[-7:]  # Last week
        most_common = Counter(recent_clusters).most_common(1)[0]
        stability = most_common[1] / len(recent_clusters)
        
        return stability
    
    async def _detect_behavioral_anomalies(self, features):
        """Detect anomalous behavior patterns"""
        if len(features) < 5:
            return []
        
        # Use recent data for anomaly detection
        recent_features = features[-14:]  # Last 2 weeks
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(recent_features)
        
        # Detect anomalies using statistical methods
        anomalies = []
        
        # Check for sudden usage spikes
        usage_trend = recent_features[:, 0]  # Daily usage
        if len(usage_trend) > 3:
            recent_avg = np.mean(usage_trend[-3:])
            historical_avg = np.mean(usage_trend[:-3])
            
            if recent_avg > historical_avg * 1.5:
                anomalies.append({
                    "type": "usage_spike",
                    "severity": "high" if recent_avg > historical_avg * 2 else "medium",
                    "description": f"Usage increased by {((recent_avg/historical_avg - 1) * 100):.1f}%"
                })
        
        # Check for unusual time patterns
        night_usage = recent_features[:, 8]  # Night sessions
        if np.mean(night_usage[-3:]) > np.mean(night_usage[:-3]) * 2:
            anomalies.append({
                "type": "night_usage_increase",
                "severity": "medium",
                "description": "Significant increase in late-night usage"
            })
        
        # Check for binge behavior
        binge_scores = recent_features[:, 11]
        if np.mean(binge_scores[-3:]) > 0.3:
            anomalies.append({
                "type": "binge_behavior",
                "severity": "high",
                "description": "Increased binge usage patterns detected"
            })
        
        return anomalies
    
    async def _analyze_usage_patterns(self, behavior_data):
        """Analyze detailed usage patterns"""
        if not behavior_data:
            return {}
        
        # Time-based patterns
        hourly_usage = defaultdict(float)
        daily_usage = defaultdict(float)
        app_usage = defaultdict(float)
        
        for entry in behavior_data:
            hour_key = entry["hour"]
            day_key = entry["day_of_week"]
            app_key = entry["app_name"]
            
            hourly_usage[hour_key] += entry["duration"]
            daily_usage[day_key] += entry["duration"]
            app_usage[app_key] += entry["duration"]
        
        # Find peak usage times
        peak_hour = max(hourly_usage, key=hourly_usage.get) if hourly_usage else 0
        peak_day = max(daily_usage, key=daily_usage.get) if daily_usage else 0
        
        # Calculate pattern consistency
        consistency_score = self._calculate_pattern_consistency(behavior_data)
        
        return {
            "peak_usage_hour": peak_hour,
            "peak_usage_day": peak_day,
            "hourly_distribution": dict(hourly_usage),
            "daily_distribution": dict(daily_usage),
            "app_distribution": dict(sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]),
            "consistency_score": consistency_score,
            "usage_variability": self._calculate_usage_variability(behavior_data)
        }
    
    def _calculate_pattern_consistency(self, behavior_data):
        """Calculate how consistent usage patterns are"""
        # Group by day and calculate daily totals
        daily_totals = defaultdict(float)
        for entry in behavior_data:
            day_key = entry["timestamp"].date()
            daily_totals[day_key] += entry["duration"]
        
        if len(daily_totals) < 7:
            return 0.5
        
        # Calculate coefficient of variation
        values = list(daily_totals.values())
        mean_usage = np.mean(values)
        std_usage = np.std(values)
        
        if mean_usage == 0:
            return 0
        
        cv = std_usage / mean_usage
        consistency = max(0, 1 - cv)  # Lower CV = higher consistency
        
        return consistency
    
    def _calculate_usage_variability(self, behavior_data):
        """Calculate usage variability metrics"""
        # Session duration variability
        durations = [entry["duration"] for entry in behavior_data]
        duration_cv = np.std(durations) / np.mean(durations) if np.mean(durations) > 0 else 0
        
        # Time variability (how spread out usage is throughout the day)
        hours = [entry["hour"] for entry in behavior_data]
        hour_spread = len(set(hours))
        
        return {
            "duration_variability": duration_cv,
            "time_spread": hour_spread / 24,  # Normalized to 0-1
            "session_regularity": 1 - duration_cv  # Inverse of variability
        }
    
    async def _generate_behavioral_insights(self, cluster_analysis, anomalies, pattern_analysis):
        """Generate behavioral insights"""
        insights = []
        
        # Cluster-based insights
        cluster_name = cluster_analysis.get("cluster_name", "Unknown")
        if cluster_name == "Heavy User":
            insights.append({
                "type": "usage_level",
                "message": "You're classified as a heavy user. Consider setting daily limits.",
                "priority": "high"
            })
        elif cluster_name == "Binge User":
            insights.append({
                "type": "usage_pattern",
                "message": "Binge usage patterns detected. Try breaking sessions into smaller chunks.",
                "priority": "high"
            })
        
        # Anomaly-based insights
        for anomaly in anomalies:
            insights.append({
                "type": "anomaly",
                "message": f"Anomaly detected: {anomaly['description']}",
                "priority": anomaly["severity"]
            })
        
        # Pattern-based insights
        peak_hour = pattern_analysis.get("peak_usage_hour", 0)
        if peak_hour >= 22 or peak_hour <= 6:
            insights.append({
                "type": "time_pattern",
                "message": "Peak usage during late night/early morning may affect sleep.",
                "priority": "medium"
            })
        
        consistency = pattern_analysis.get("consistency_score", 0)
        if consistency < 0.3:
            insights.append({
                "type": "consistency",
                "message": "Highly variable usage patterns. Consider establishing routines.",
                "priority": "low"
            })
        
        return insights
    
    async def _generate_behavioral_recommendations(self, insights):
        """Generate personalized recommendations based on behavioral insights"""
        recommendations = []
        
        # Priority-based recommendations
        high_priority_insights = [i for i in insights if i.get("priority") == "high"]
        
        if high_priority_insights:
            recommendations.extend([
                "Set strict daily usage limits",
                "Use app blocking during peak hours",
                "Schedule regular digital detox periods"
            ])
        
        # Pattern-specific recommendations
        for insight in insights:
            if insight["type"] == "time_pattern":
                recommendations.append("Enable night mode and usage restrictions after 9 PM")
            elif insight["type"] == "usage_pattern":
                recommendations.append("Use the Pomodoro technique: 25 min usage, 5 min break")
            elif insight["type"] == "consistency":
                recommendations.append("Create a structured daily routine for device usage")
        
        # General recommendations
        recommendations.extend([
            "Try mindful gaming alternatives",
            "Set up break reminders every 30 minutes",
            "Use voice notifications for usage awareness"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _update_user_profile(self, user_id: str, features, insights):
        """Update user behavioral profile"""
        if len(features) == 0:
            return
        
        profile = {
            "last_updated": datetime.now(),
            "behavior_summary": {
                "avg_daily_usage": float(np.mean(features[:, 0])),
                "avg_sessions": float(np.mean(features[:, 1])),
                "app_diversity": float(np.mean(features[:, 2])),
                "binge_tendency": float(np.mean(features[:, 11]))
            },
            "risk_factors": [i for i in insights if i.get("priority") == "high"],
            "improvement_areas": [i["type"] for i in insights]
        }
        
        self.user_profiles[user_id] = profile