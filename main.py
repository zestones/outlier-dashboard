import pandas as pd
import streamlit as st

from src.data.parse import process_data
from src.tabs.calendar_view import calendar_view_tab
from src.tabs.earnings_analysis import earnings_analysis_tab
from src.tabs.hours_analysis import display_hours_analysis_tab
from src.tabs.overview import display_overview_tab
from src.tabs.projects_details import projects_details_tab
from src.tabs.raw_data import raw_data_tab
from src.utils.styling import DashboardStyle

# Set page configuration
st.set_page_config(
    page_title="Work Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

# Apply theme using the DashboardStyle class
theme = DashboardStyle.init_theme_selector()

# Main title in the content area
st.title("Work Analysis Dashboard")
st.markdown("View and analyze your work hours, earnings, and performance metrics")


def main():
    # Create sidebar for file upload and controls
    with st.sidebar:
        st.header("Data Source")
        st.markdown("Upload your work data to begin analysis")
        # File upload widget in sidebar
        uploaded_file = st.file_uploader("Upload your work data CSV", type=["csv"])

    # Main content area
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
    else:
        # Display instructions when no file is uploaded
        st.info(
            "👈 Please upload your Outlier CSV file from the sidebar to start the analysis"
        )

        # Optional: Add some placeholder content or sample visualizations
        st.markdown(
            """
        ### Welcome to the Work Analysis Dashboard
        
        This dashboard helps you analyze your Outlier work data to gain insights into:
        - Working hours patterns
        - Earnings distribution
        - Project performance metrics
        - Time management analytics
        
        To begin, upload your Outlier CSV file containing work data in the sidebar.
        """
        )


if __name__ == "__main__":
    main()
