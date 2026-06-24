import pandas as pd

def load_data(file_path):
    """Load CSV file"""
    return pd.read_csv(file_path)


def summary_stats(df):
    """Basic statistics"""
    return df.describe()


def missing_values(df):
    """Check missing values"""
    return df.isnull().sum()


def correlation(df):
    """Correlation matrix"""
    return df.corr(numeric_only=True)


def top_performers(df):
    """Return top students by score"""
    return df.sort_values(by="Score", ascending=False).head(3)