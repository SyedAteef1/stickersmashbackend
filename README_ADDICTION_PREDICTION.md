# Addiction Risk Prediction System

## Overview
ML-powered system that predicts addiction risk levels and provides smart insights with 3-day graphical comparison.

## Features

### 1. **Addiction Risk Prediction**
- Gradient Boosting ML model for risk assessment
- 4 risk levels: Low (0), Moderate (1), High (2), Critical (3)
- Rule-based fallback for untrained scenarios

### 2. **Smart Insights**
- **Trend Analysis**: Detects increasing/decreasing usage patterns
- **Night Usage Alerts**: Identifies sleep-disrupting behavior
- **Binge Detection**: Flags extended usage sessions (>45 min)
- **Social Media Dependency**: Monitors excessive social app usage

### 3. **3-Day Graphical Comparison**
Four visualization charts:
- **Daily Usage Bar Chart**: Total minutes with risk thresholds
- **Time Distribution**: Usage by morning/afternoon/evening/night
- **Risk Progression**: Line chart showing risk level changes
- **App Categories**: Pie charts for social/entertainment/productivity breakdown

### 4. **Actionable Recommendations**
- Personalized based on risk level and detected patterns
- Includes usage limits, app timers, and behavioral suggestions

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run demo
python demo_addiction_analysis.py
```

## Usage

```python
from addiction_predictor import analyze_addiction_risk
from usage_tracker import UsageDataProcessor

# Process your usage logs
three_day_data = UsageDataProcessor.get_three_day_data(raw_logs)

# Analyze addiction risk
results = analyze_addiction_risk(three_day_data)

print(f"Risk Level: {results['current_risk']['risk_label']}")
print(f"Insights: {results['insights']}")
print(f"Visualization: {results['visualization']}")
```

## Data Format

Each day's data should include:
```python
{
    'total_duration': 240,        # Total minutes
    'session_count': 15,          # Number of sessions
    'night_usage': 45,            # Minutes after 10 PM
    'binge_sessions': 2,          # Sessions > 45 min
    'social_media_time': 120,     # Social app minutes
    'entertainment_time': 80,     # Entertainment minutes
    'morning_usage': 30,          # 6 AM - 12 PM
    'afternoon_usage': 90,        # 12 PM - 6 PM
    'evening_usage': 75,          # 6 PM - 10 PM
    # ... other metrics
}
```

## Risk Calculation

**Rule-Based Scoring:**
- Daily usage > 6 hours: +3 points
- Daily usage > 4 hours: +2 points
- Night usage > 1 hour: +2 points
- Binge sessions > 3: +2 points

**Risk Levels:**
- 0-1 points: Low Risk
- 2-3 points: Moderate Risk
- 4-5 points: High Risk
- 6+ points: Critical Risk

## Output

The system generates:
1. **Risk Assessment**: Current risk level with probability
2. **Smart Insights**: 3-5 actionable insights with severity
3. **Visual Report**: PNG file with 4 comparison charts
4. **Recommendations**: Personalized action items

## Integration with Behavior Analyzer

```python
from behavior_analyzer import BehaviorAnalyzer
from addiction_predictor import analyze_addiction_risk

# Get behavior data
analyzer = BehaviorAnalyzer()
behavior_data = await analyzer.analyze_behavior(user_id)

# Convert to addiction analysis format
three_day_data = convert_behavior_to_daily(behavior_data)

# Analyze addiction risk
results = analyze_addiction_risk(three_day_data)
```

## Files

- `addiction_predictor.py`: Main ML model and analysis engine
- `usage_tracker.py`: Data processing and aggregation
- `demo_addiction_analysis.py`: Demo script with sample data
- `behavior_analyzer.py`: Existing behavior analysis (integration point)

## Example Output

```
ADDICTION RISK PREDICTION & ANALYSIS
============================================================

📅 Daily Usage Summary:
Day 1: 245 min (4.1 hours) | 12 sessions | 3 binge
Day 2: 312 min (5.2 hours) | 15 sessions | 5 binge
Day 3: 378 min (6.3 hours) | 18 sessions | 6 binge

⚠️  Current Risk Level: HIGH
   Risk Score: 2/3
   Probability: 78.5%

💡 Smart Insights:
1. ⚠️ Usage increasing by 67 min/day
2. 🚨 14 binge sessions detected in 3 days
3. ⚠️ High social media usage: 195 min/day

📋 Recommendations:
1. Set daily usage limits (max 3-4 hours)
2. Take 10-min breaks every hour
3. Enable app timers for social media
```

## Customization

Adjust thresholds in `addiction_predictor.py`:
```python
# Risk thresholds
DAILY_LIMIT = 240  # 4 hours
NIGHT_LIMIT = 60   # 1 hour
BINGE_THRESHOLD = 45  # minutes
```
