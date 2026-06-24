from tools import (
    load_data,
    summary_stats,
    missing_values,
    correlation,
    top_performers
)

from utils import plot_scores, plot_study_vs_score
from adk_client import GeminiClient

class DataAnalystAgent:

    def __init__(self, file_path):
        self.df = load_data(file_path)
        self.llm = GeminiClient()

    def analyze(self):
        print("\n📊 SUMMARY STATS:\n")
        print(summary_stats(self.df))

        print("\n❗ MISSING VALUES:\n")
        print(missing_values(self.df))

        print("\n📈 CORRELATION:\n")
        print(correlation(self.df))

        print("\n🏆 TOP PERFORMERS:\n")
        print(top_performers(self.df))

        # charts
        plot_scores(self.df)
        plot_study_vs_score(self.df)

    def insights(self):
        prompt = f"""
You are an expert AI Data Analyst Agent.

Analyze this dataset and give:
1. Key insights
2. Trends
3. Recommendations for improvement

DATA:
{self.df.to_string(index=False)}
"""

        result = self.llm.generate(prompt)

        print("\n🧠 AI INSIGHTS:\n")
        print(result)