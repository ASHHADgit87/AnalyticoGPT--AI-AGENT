import streamlit as st

def render_insights_layout():
    st.markdown('<div class="main-header">🧠 CRITICAL AI NARRATIVE INSIGHTS</div>', unsafe_allow_html=True)
    
    if "ai_insights" in st.session_state:
        st.markdown(st.session_state["ai_insights"])
    else:
        sample_insights = """
        ### **1. Key Insights**
        * **Strong Positive Correlation between Study Hours and Scores:** Clear functional trajectory mapped between input effort metrics ($0.927$) and evaluation score outputs.
        * **Performance Gap for Similar Effort:** Divergences identified indicating third-variable variances.
        """
        st.markdown(sample_insights)