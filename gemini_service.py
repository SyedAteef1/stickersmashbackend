import google.generativeai as genai
import json
from typing import Dict, List, Any

class GeminiInsightsService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            'gemini-pro',
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=500,
                top_p=0.8
            )
        )
    
    def generate_insights(self, usage_data: List[Dict], user_id: str) -> Dict[str, Any]:
        """Generate AI-powered insights using Gemini"""
        
        # Prepare usage summary
        total_usage = sum(day.get('total_duration', 0) for day in usage_data)
        avg_daily = total_usage / len(usage_data) if usage_data else 0
        
        # Get top apps
        app_usage = {}
        for day in usage_data:
            for app, time in day.get('app_usage', {}).items():
                app_usage[app] = app_usage.get(app, 0) + time
        
        top_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Simplified prompt for faster response
        prompt = f"""
Analyze screen time: {avg_daily:.0f}min/day average. Top apps: {', '.join([f"{app}:{time}min" for app, time in top_apps[:3]])}

Return JSON with:
{{"insights": ["observation1", "observation2"], "precautions": ["tip1", "tip2"], "recommendations": ["action1", "action2"], "risk_factors": ["risk1"]}}

Focus on which apps are overused and specific prevention advice. Keep responses under 20 words each.
"""
        
        try:
            response = self.model.generate_content(prompt)
            # Clean response text
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:-3]
            elif text.startswith('```'):
                text = text[3:-3]
            
            result = json.loads(text)
            
            return {
                'ai_insights': result.get('insights', [])[:3],
                'precautions': result.get('precautions', [])[:3],
                'recommendations': result.get('recommendations', [])[:3],
                'risk_factors': result.get('risk_factors', [])[:2],
                'generated_at': usage_data[-1].get('date') if usage_data else None
            }
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Always return fallback insights to prevent crashes
            return self._fallback_insights(usage_data, top_apps)
    
    def _fallback_insights(self, usage_data: List[Dict], top_apps: List[tuple]) -> Dict[str, Any]:
        """Fast fallback insights if Gemini API fails"""
        avg_daily = sum(day.get('total_duration', 0) for day in usage_data) / len(usage_data)
        
        insights = []
        precautions = []
        recommendations = []
        risk_factors = []
        
        if avg_daily > 240:
            insights.append(f"High usage: {avg_daily:.0f}min/day detected")
            precautions.append("Set daily limits under 4 hours")
            risk_factors.append("Excessive screen time")
        
        if top_apps:
            top_app, top_time = top_apps[0]
            insights.append(f"{top_app}: {top_time}min - most used app")
            recommendations.append(f"Limit {top_app} to 30min sessions")
        
        if len(top_apps) > 1:
            recommendations.append("Use app timers for top 3 apps")
            precautions.append("Take breaks every 45 minutes")
        
        return {
            'ai_insights': insights[:2],
            'precautions': precautions[:2],
            'recommendations': recommendations[:2],
            'risk_factors': risk_factors[:1],
            'generated_at': usage_data[-1].get('date') if usage_data else None
        }