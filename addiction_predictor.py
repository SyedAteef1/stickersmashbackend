import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

class AddictionRiskPredictor:
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, usage_data):
        """Extract addiction risk features from usage data"""
        features = []
        for day_data in usage_data:
            daily_usage = day_data.get('total_duration', 0)
            session_count = day_data.get('session_count', 0)
            night_usage = day_data.get('night_usage', 0)
            avg_session = daily_usage / session_count if session_count > 0 else 0
            
            features.append([
                daily_usage,
                session_count,
                night_usage,
                avg_session,
                day_data.get('binge_sessions', 0),
                day_data.get('social_media_time', 0),
                day_data.get('max_continuous_usage', 0)
            ])
        return np.array(features)
    
    def train(self, X, y):
        """Train the addiction risk model"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
    
    def predict_risk(self, usage_data):
        """Predict addiction risk level"""
        if not self.is_trained:
            # Use rule-based system if not trained
            return self._rule_based_prediction(usage_data)
        
        features = self.extract_features([usage_data])
        X_scaled = self.scaler.transform(features)
        risk_prob = self.model.predict_proba(X_scaled)[0]
        risk_level = self.model.predict(X_scaled)[0]
        
        return {
            'risk_level': int(risk_level),
            'risk_probability': float(risk_prob[risk_level]),
            'risk_label': self._get_risk_label(risk_level)
        }
    
    def _rule_based_prediction(self, usage_data):
        """Rule-based risk assessment"""
        daily_usage = usage_data.get('total_duration', 0)
        night_usage = usage_data.get('night_usage', 0)
        binge_sessions = usage_data.get('binge_sessions', 0)
        
        risk_score = 0
        if daily_usage > 360: risk_score += 3  # >6 hours
        elif daily_usage > 240: risk_score += 2  # >4 hours
        elif daily_usage > 120: risk_score += 1  # >2 hours
        
        if night_usage > 60: risk_score += 2
        if binge_sessions > 3: risk_score += 2
        
        risk_level = min(risk_score, 3)
        
        return {
            'risk_level': risk_level,
            'risk_probability': min(risk_score / 7, 1.0),
            'risk_label': self._get_risk_label(risk_level)
        }
    
    def _get_risk_label(self, level):
        labels = {0: 'Low', 1: 'Moderate', 2: 'High', 3: 'Critical'}
        return labels.get(level, 'Unknown')
    
    def generate_insights(self, three_day_data):
        """Generate smart insights from 3-day data"""
        insights = []
        
        # Trend analysis
        daily_usage = [d.get('total_duration', 0) for d in three_day_data]
        if len(daily_usage) >= 2:
            trend = np.polyfit(range(len(daily_usage)), daily_usage, 1)[0]
            if trend > 30:
                insights.append({
                    'type': 'warning',
                    'message': f'Usage increasing by {trend:.0f} min/day',
                    'severity': 'high'
                })
            elif trend < -30:
                insights.append({
                    'type': 'positive',
                    'message': f'Usage decreasing by {abs(trend):.0f} min/day',
                    'severity': 'low'
                })
        
        # Night usage pattern
        night_usage = [d.get('night_usage', 0) for d in three_day_data]
        avg_night = np.mean(night_usage)
        if avg_night > 60:
            insights.append({
                'type': 'warning',
                'message': f'High night usage: {avg_night:.0f} min/day affects sleep',
                'severity': 'high'
            })
        
        # Binge behavior
        total_binge = sum(d.get('binge_sessions', 0) for d in three_day_data)
        if total_binge > 5:
            insights.append({
                'type': 'alert',
                'message': f'{total_binge} binge sessions detected in 3 days',
                'severity': 'critical'
            })
        
        # Social media dependency
        social_time = [d.get('social_media_time', 0) for d in three_day_data]
        avg_social = np.mean(social_time)
        if avg_social > 180:
            insights.append({
                'type': 'warning',
                'message': f'High social media usage: {avg_social:.0f} min/day',
                'severity': 'moderate'
            })
        
        return insights
    
    def visualize_comparison(self, three_day_data, save_path='addiction_analysis.png'):
        """Create graphical comparison of 3-day usage data"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('3-Day Addiction Risk Analysis', fontsize=16, fontweight='bold')
        
        days = ['Day 1', 'Day 2', 'Day 3']
        
        # 1. Daily Usage Comparison
        daily_usage = [d.get('total_duration', 0) for d in three_day_data]
        colors = ['#2ecc71' if u < 180 else '#f39c12' if u < 300 else '#e74c3c' for u in daily_usage]
        axes[0, 0].bar(days, daily_usage, color=colors, alpha=0.7)
        axes[0, 0].axhline(y=240, color='r', linestyle='--', label='Risk Threshold (4h)')
        axes[0, 0].set_ylabel('Minutes')
        axes[0, 0].set_title('Total Daily Usage')
        axes[0, 0].legend()
        
        # 2. Usage Distribution by Time of Day
        time_categories = ['Morning', 'Afternoon', 'Evening', 'Night']
        time_data = np.array([[
            d.get('morning_usage', 0),
            d.get('afternoon_usage', 0),
            d.get('evening_usage', 0),
            d.get('night_usage', 0)
        ] for d in three_day_data])
        
        x = np.arange(len(days))
        width = 0.2
        for i, category in enumerate(time_categories):
            axes[0, 1].bar(x + i*width, time_data[:, i], width, label=category)
        axes[0, 1].set_xlabel('Days')
        axes[0, 1].set_ylabel('Minutes')
        axes[0, 1].set_title('Usage by Time of Day')
        axes[0, 1].set_xticks(x + width * 1.5)
        axes[0, 1].set_xticklabels(days)
        axes[0, 1].legend()
        
        # 3. Risk Level Progression
        risk_levels = [self.predict_risk(d)['risk_level'] for d in three_day_data]
        risk_colors = ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c']
        axes[1, 0].plot(days, risk_levels, marker='o', linewidth=2, markersize=10, color='#3498db')
        axes[1, 0].fill_between(range(len(days)), risk_levels, alpha=0.3, color='#3498db')
        axes[1, 0].set_ylabel('Risk Level (0-3)')
        axes[1, 0].set_title('Addiction Risk Progression')
        axes[1, 0].set_ylim(-0.5, 3.5)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. App Category Breakdown
        categories = ['Social Media', 'Entertainment', 'Productivity', 'Other']
        category_data = np.array([[
            d.get('social_media_time', 0),
            d.get('entertainment_time', 0),
            d.get('productivity_time', 0),
            d.get('other_time', 0)
        ] for d in three_day_data])
        
        for i, day in enumerate(days):
            axes[1, 1].pie(category_data[i], labels=categories if i == 0 else None,
                          autopct='%1.0f%%', startangle=90, radius=0.8 - i*0.2)
        axes[1, 1].set_title('App Category Distribution')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path


def analyze_addiction_risk(user_data):
    """Main function to analyze addiction risk with insights and visualization"""
    predictor = AddictionRiskPredictor()
    
    # Generate insights
    insights = predictor.generate_insights(user_data)
    
    # Predict current risk
    current_risk = predictor.predict_risk(user_data[-1])
    
    # Create visualization
    viz_path = predictor.visualize_comparison(user_data)
    
    return {
        'current_risk': current_risk,
        'insights': insights,
        'visualization': viz_path,
        'recommendations': _generate_recommendations(current_risk, insights)
    }


def _generate_recommendations(risk_data, insights):
    """Generate actionable recommendations"""
    recommendations = []
    
    risk_level = risk_data['risk_level']
    
    if risk_level >= 2:
        recommendations.append('Set daily usage limits (max 3-4 hours)')
        recommendations.append('Enable app timers for social media')
        recommendations.append('Schedule device-free hours')
    
    if any(i['type'] == 'warning' and 'night' in i['message'].lower() for i in insights):
        recommendations.append('Avoid screens 1 hour before bedtime')
        recommendations.append('Enable night mode/blue light filter')
    
    if any('binge' in i['message'].lower() for i in insights):
        recommendations.append('Take 10-min breaks every hour')
        recommendations.append('Use focus mode during work/study')
    
    if not recommendations:
        recommendations.append('Maintain current healthy usage patterns')
    
    return recommendations
