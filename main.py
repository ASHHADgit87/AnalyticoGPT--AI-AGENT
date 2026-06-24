from agent import DataAnalystAgent

def main():
    print("\n🤖 AI DATA ANALYST AGENT STARTED\n")

    agent = DataAnalystAgent("sample.csv")

    agent.analyze()
    agent.insights()

if __name__ == "__main__":
    main()