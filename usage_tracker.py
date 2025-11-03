import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class UsageDataProcessor:
    """Process and aggregate usage data for addiction analysis"""
    
    @staticmethod
    def aggregate_daily_data(raw_logs, target_date):
        """Aggregate raw usage logs into daily metrics"""
        daily_sessions = [log for log in raw_logs 
                         if log['timestamp'].date() == target_date]
        
        if not daily_sessions:
            return None
        
        # Calculate metrics
        total_duration = sum(s.get('duration', 0) for s in daily_sessions)
        session_count = len(daily_sessions)
        
        # Time-based usage
        morning_usage = sum(s['duration'] for s in daily_sessions if 6 <= s['timestamp'].hour < 12)
        afternoon_usage = sum(s['duration'] for s in daily_sessions if 12 <= s['timestamp'].hour < 18)
        evening_usage = sum(s['duration'] for s in daily_sessions if 18 <= s['timestamp'].hour < 22)
        night_usage = sum(s['duration'] for s in daily_sessions if s['timestamp'].hour >= 22 or s['timestamp'].hour < 6)
        
        # Binge detection (sessions > 45 min)
        binge_sessions = sum(1 for s in daily_sessions if s.get('duration', 0) > 45)
        
        # Max continuous usage
        sorted_sessions = sorted(daily_sessions, key=lambda x: x['timestamp'])
        max_continuous = UsageDataProcessor._calculate_max_continuous(sorted_sessions)
        
        # App categories
        social_apps = {'Instagram', 'TikTok', 'WhatsApp', 'Facebook', 'Twitter', 'Snapchat'}
        entertainment_apps = {'YouTube', 'Netflix', 'Spotify', 'Games', 'Twitch'}
        productivity_apps = {'Chrome', 'Email', 'Calendar', 'Notes', 'Office'}
        
        social_media_time = sum(s['duration'] for s in daily_sessions if s.get('app_name') in social_apps)
        entertainment_time = sum(s['duration'] for s in daily_sessions if s.get('app_name') in entertainment_apps)
        productivity_time = sum(s['duration'] for s in daily_sessions if s.get('app_name') in productivity_apps)
        other_time = total_duration - social_media_time - entertainment_time - productivity_time
        
        return {
            'date': target_date,
            'total_duration': total_duration,
            'session_count': session_count,
            'morning_usage': morning_usage,
            'afternoon_usage': afternoon_usage,
            'evening_usage': evening_usage,
            'night_usage': night_usage,
            'binge_sessions': binge_sessions,
            'max_continuous_usage': max_continuous,
            'social_media_time': social_media_time,
            'entertainment_time': entertainment_time,
            'productivity_time': productivity_time,
            'other_time': max(0, other_time)
        }
    
    @staticmethod
    def _calculate_max_continuous(sorted_sessions):
        """Calculate maximum continuous usage time"""
        if not sorted_sessions:
            return 0
        
        max_continuous = 0
        current_continuous = sorted_sessions[0].get('duration', 0)
        
        for i in range(1, len(sorted_sessions)):
            time_gap = (sorted_sessions[i]['timestamp'] - sorted_sessions[i-1]['timestamp']).total_seconds() / 60
            
            if time_gap < 5:  # Less than 5 min gap = continuous
                current_continuous += sorted_sessions[i].get('duration', 0)
            else:
                max_continuous = max(max_continuous, current_continuous)
                current_continuous = sorted_sessions[i].get('duration', 0)
        
        return max(max_continuous, current_continuous)
    
    @staticmethod
    def get_three_day_data(raw_logs):
        """Get aggregated data for last 3 days"""
        today = datetime.now().date()
        three_day_data = []
        
        for i in range(2, -1, -1):  # Day 1, Day 2, Day 3
            target_date = today - timedelta(days=i)
            daily_data = UsageDataProcessor.aggregate_daily_data(raw_logs, target_date)
            
            if daily_data:
                three_day_data.append(daily_data)
            else:
                # Generate minimal data if no logs
                three_day_data.append({
                    'date': target_date,
                    'total_duration': 0,
                    'session_count': 0,
                    'morning_usage': 0,
                    'afternoon_usage': 0,
                    'evening_usage': 0,
                    'night_usage': 0,
                    'binge_sessions': 0,
                    'max_continuous_usage': 0,
                    'social_media_time': 0,
                    'entertainment_time': 0,
                    'productivity_time': 0,
                    'other_time': 0
                })
        
        return three_day_data
    
    def process_logs_to_daily(self, logs):
        """Convert raw logs to daily aggregated data with app usage details"""
        daily_data = {}
        
        for log in logs:
            date = log['timestamp'].date()
            if date not in daily_data:
                daily_data[date] = {
                    'date': str(date),
                    'total_duration': 0,
                    'session_count': 0,
                    'app_usage': {},
                    'night_usage': 0,
                    'morning_usage': 0,
                    'afternoon_usage': 0,
                    'evening_usage': 0,
                    'binge_sessions': 0,
                    'social_media_time': 0,
                    'entertainment_time': 0,
                    'productivity_time': 0,
                    'other_time': 0,
                    'max_continuous_usage': 0
                }
            
            day_data = daily_data[date]
            day_data['total_duration'] += log['duration']
            day_data['session_count'] += 1
            
            # Track app usage
            app_name = log['app_name']
            day_data['app_usage'][app_name] = day_data['app_usage'].get(app_name, 0) + log['duration']
            
            # Time-based categorization
            hour = log['timestamp'].hour
            if 22 <= hour or hour <= 6:
                day_data['night_usage'] += log['duration']
            elif 6 < hour <= 12:
                day_data['morning_usage'] += log['duration']
            elif 12 < hour <= 18:
                day_data['afternoon_usage'] += log['duration']
            else:
                day_data['evening_usage'] += log['duration']
            
            # App categorization
            if app_name.lower() in ['instagram', 'facebook', 'twitter', 'snapchat', 'tiktok']:
                day_data['social_media_time'] += log['duration']
            elif app_name.lower() in ['youtube', 'netflix', 'spotify', 'games']:
                day_data['entertainment_time'] += log['duration']
            elif app_name.lower() in ['email', 'calendar', 'notes', 'documents']:
                day_data['productivity_time'] += log['duration']
            else:
                day_data['other_time'] += log['duration']
        
        return list(daily_data.values())
    
    def generate_sample_data(self, days=7):
        """Generate sample usage data for testing"""
        sample_data = []
        for i in range(days):
            sample_data.append({
                'date': f'Day {i+1}',
                'total_duration': 180 + (i * 30),
                'session_count': 15 + i,
                'app_usage': {
                    'Instagram': 60 + (i * 10),
                    'YouTube': 45 + (i * 8),
                    'WhatsApp': 30 + (i * 5),
                    'Chrome': 25 + (i * 3),
                    'TikTok': 20 + (i * 4)
                },
                'night_usage': 30 + (i * 5),
                'morning_usage': 40,
                'afternoon_usage': 60,
                'evening_usage': 50,
                'binge_sessions': i,
                'social_media_time': 80 + (i * 14),
                'entertainment_time': 65 + (i * 8),
                'productivity_time': 25,
                'other_time': 10,
                'max_continuous_usage': 45 + (i * 5)
            })
        return sample_data


def generate_sample_data():
    """Generate sample usage data for testing"""
    np.random.seed(42)
    logs = []
    
    for day_offset in range(3):
        base_date = datetime.now() - timedelta(days=2-day_offset)
        sessions = np.random.randint(8, 20)
        
        for _ in range(sessions):
            timestamp = base_date.replace(
                hour=np.random.randint(6, 24),
                minute=np.random.randint(0, 60),
                second=0
            )
            
            logs.append({
                'timestamp': timestamp,
                'app_name': np.random.choice([
                    'Instagram', 'TikTok', 'YouTube', 'WhatsApp',
                    'Chrome', 'Games', 'Netflix', 'Spotify'
                ]),
                'duration': np.random.exponential(20) + 5
            })
    
    return sorted(logs, key=lambda x: x['timestamp'])
