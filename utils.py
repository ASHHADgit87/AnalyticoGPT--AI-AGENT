import matplotlib.pyplot as plt

def plot_scores(df):
    plt.figure()
    plt.bar(df["Name"], df["Score"])
    plt.title("Student Scores")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def plot_study_vs_score(df):
    plt.figure()
    plt.scatter(df["Hours_Studied"], df["Score"])
    plt.title("Study Hours vs Score")
    plt.xlabel("Hours Studied")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.show()