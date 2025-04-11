import pandas as pd
import streamlit as st

from src.data.parse import process_data
from src.tabs.calendar_view import calendar_view_tab
from src.tabs.earnings_analysis import earnings_analysis_tab
from src.tabs.hours_analysis import display_hours_analysis_tab
from src.tabs.overview import display_overview_tab
from src.tabs.projects_details import projects_details_tab
from src.tabs.raw_data import raw_data_tab

# Set page configuration
st.set_page_config(
    page_title="Work Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
<style>
    .main {
        padding: 1rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4e8df5;
        color: white;
    }
    .metric-card {
        background-color: #f9f9f9;
        border: 1px solid #eaeaea;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        margin-top: 10px;
    }
    .metric-title {
        color: #555;
        font-size: 14px;
    }
    hr {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .status-pending {
        color: #FFA500;
        font-weight: bold;
    }
    .status-processed {
        color: #008000;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Title of the app
st.title("📊 Work Analytics Dashboard")
st.markdown(
    "Upload your work data CSV file to analyze work hours, earnings, and performance metrics"
)


def main():
    # File upload widget
    uploaded_file = st.file_uploader("Upload your work data CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df = process_data(df)

            # Create tabs for different analysis aspects
            tabs = st.tabs(
                [
                    "📈 Overview",
                    "⏱️ Hours Analysis",
                    "💰 Earnings Analysis",
                    "📋 Project & Task Details",
                    "📆 Calendar View",
                    "🔍 Raw Data",
                ]
            )

            # Tab 1: Overview
            with tabs[0]:
                display_overview_tab(df)

            # Tab 2: Hours Analysis
            with tabs[1]:
                display_hours_analysis_tab(df)
            # Tab 3: Earnings Analysis
            with tabs[2]:
                earnings_analysis_tab(df)

            # Tab 4: Project & Task Details
            with tabs[3]:
                projects_details_tab(df)

            # Tab 5: Calendar View
            with tabs[4]:
                calendar_view_tab(df)
            # Tab 6: Raw Data
            with tabs[5]:
                raw_data_tab(df)

        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")
            st.write("Please make sure the uploaded file is in the correct format.")


if __name__ == "__main__":
    main()
