"""
Demo script for Addiction Risk Prediction with 3-Day Comparison
"""
from addiction_predictor import AddictionRiskPredictor, analyze_addiction_risk
from usage_tracker import UsageDataProcessor, generate_sample_data

def main():
    print("=" * 60)
    print("ADDICTION RISK PREDICTION & ANALYSIS")
    print("=" * 60)
    
    # Generate sample data
    print("\n📊 Generating 3-day usage data...")
    raw_logs = generate_sample_data()
    
    # Process data
    processor = UsageDataProcessor()
    three_day_data = processor.get_three_day_data(raw_logs)
    
    # Display daily summaries
    print("\n📅 Daily Usage Summary:")
    print("-" * 60)
    for i, day_data in enumerate(three_day_data, 1):
        print(f"\nDay {i} ({day_data['date']}):")
        print(f"  Total Usage: {day_data['total_duration']:.0f} minutes ({day_data['total_duration']/60:.1f} hours)")
        print(f"  Sessions: {day_data['session_count']}")
        print(f"  Night Usage: {day_data['night_usage']:.0f} min")
        print(f"  Binge Sessions: {day_data['binge_sessions']}")
        print(f"  Social Media: {day_data['social_media_time']:.0f} min")
    
    # Analyze addiction risk
    print("\n\n🔍 Analyzing Addiction Risk...")
    print("-" * 60)
    
    predictor = AddictionRiskPredictor()
    results = analyze_addiction_risk(three_day_data)
    
    # Display risk assessment
    risk = results['current_risk']
    print(f"\n⚠️  Current Risk Level: {risk['risk_label'].upper()}")
    print(f"   Risk Score: {risk['risk_level']}/3")
    print(f"   Probability: {risk['risk_probability']*100:.1f}%")
    
    # Display insights
    print("\n\n💡 Smart Insights:")
    print("-" * 60)
    if results['insights']:
        for i, insight in enumerate(results['insights'], 1):
            emoji = {'warning': '⚠️', 'alert': '🚨', 'positive': '✅'}.get(insight['type'], 'ℹ️')
            print(f"{i}. {emoji} {insight['message']}")
            print(f"   Severity: {insight['severity'].upper()}")
    else:
        print("✅ No concerning patterns detected")
    
    # Display recommendations
    print("\n\n📋 Recommendations:")
    print("-" * 60)
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")
    
    # Visualization
    print("\n\n📈 Generating visual comparison...")
    print(f"   Saved to: {results['visualization']}")
    
    print("\n" + "=" * 60)
    print("Analysis Complete! Check 'addiction_analysis.png' for graphs")
    print("=" * 60)


if __name__ == "__main__":
    main()
