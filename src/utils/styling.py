import streamlit as st


class DashboardStyle:
    """
    A class to manage the styling of the dashboard with support for dark and light modes.
    """

    @staticmethod
    def get_theme_css(theme="dark"):
        """
        Generate the CSS for the dashboard based on the theme.
        Now only returns dark theme regardless of parameter.

        Parameters:
        -----------
        theme : str
            Parameter kept for compatibility, but ignored as we always use dark theme

        Returns:
        --------
        str
            The CSS to be applied to the dashboard (dark theme only)
        """
        base_css = """
            .main {
                padding: 1.5rem 2rem;
            }
            
            /* Modern tabs styling */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px;
                padding-bottom: 2px;
                border-bottom: 1px solid rgba(120, 120, 120, 0.3);
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 45px;
                white-space: pre-wrap;
                border-radius: 8px 8px 0px 0px;
                padding: 8px 16px;
                font-weight: 500;
                transition: all 0.2s ease;
                border: none;
            }
            
            /* HR separator */
            hr {
                margin: 1.5rem 0;
                opacity: 0.2;
                border: none;
                height: 1px;
            }
            
            /* File uploader */
            .stFileUploader {
                padding: 15px;
                border-radius: 12px;
                margin-bottom: 20px;
            }
            
            /* Modern buttons */
            button[kind="primary"] {
                border-radius: 8px;
                transition: all 0.2s ease;
            }
            
            button[kind="primary"]:hover {
                transform: translateY(-2px);
            }
            
            /* Date selector styling */
            .date-selector-container {
                background: linear-gradient(90deg, rgba(45, 55, 75, 0.4) 0%, rgba(45, 55, 75, 0.2) 100%);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid rgba(80, 120, 200, 0.2);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
                margin-bottom: 25px;
            }
            
            .date-selector-header {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
                border-bottom: 1px solid rgba(100, 120, 200, 0.2);
                padding-bottom: 12px;
            }
            
            .date-selector-title {
                font-size: 1.1rem;
                font-weight: 500;
                color: #e6e6e6;
                margin: 0;
                display: flex;
                align-items: center;
            }
            
            .date-selector-title svg {
                margin-right: 8px;
                color: rgba(100, 150, 255, 0.9);
            }
            
            .date-preset-grid {
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 10px;
                margin-bottom: 18px;
            }
            
            .date-preset-btn {
                background: rgba(60, 70, 90, 0.4);
                color: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(80, 100, 180, 0.3);
                border-radius: 6px;
                padding: 8px 10px;
                text-align: center;
                font-size: 0.9rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .date-preset-btn:hover {
                background: rgba(80, 110, 200, 0.3);
                border-color: rgba(100, 140, 240, 0.5);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }
            
            .date-preset-btn.active {
                background: rgba(80, 120, 230, 0.4);
                border-color: rgba(100, 150, 255, 0.6);
                color: white;
            }
            
            .date-input-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-top: 15px;
            }
            
            .date-input-label {
                font-size: 0.9rem;
                font-weight: 500;
                color: rgba(255, 255, 255, 0.7);
                margin-bottom: 5px;
                display: block;
            }
            
            .date-summary {
                background: rgba(50, 60, 80, 0.3);
                border-radius: 8px;
                padding: 10px 15px;
                margin-top: 15px;
                font-size: 0.9rem;
                display: flex;
                justify-content: space-between;
                border: 1px solid rgba(80, 100, 180, 0.15);
            }
        """

        # Dark theme specific CSS
        dark_css = """
            /* Force dark mode for the entire app */
            .stApp {
                background-color: #0e1117;
                color: #f0f2f6;
            }
            
            .stTabs [data-baseweb="tab"] {
                background-color: rgba(50, 55, 65, 0.3);
                color: rgba(255, 255, 255, 0.8);
            }
            
            .stTabs [aria-selected="true"] {
                background-color: rgba(100, 150, 255, 0.6) !important;
                color: white !important;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.25);
            }
            
            /* Modern card design */
            .metric-card {
                background-color: rgba(30, 34, 44, 0.5);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(70, 70, 70, 0.3);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                margin-bottom: 15px;
            }
            
            .metric-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
            }
            
            .metric-value {
                font-size: 28px;
                font-weight: 600;
                margin: 12px 0 8px;
                background: linear-gradient(90deg, #5e9df5, #9c6cf5);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .metric-title {
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #bbb;
                opacity: 0.8;
            }
            
            .kpi-container {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            
            .trend-indicator {
                display: flex;
                align-items: center;
                margin-top: 5px;
                font-size: 0.9rem;
            }
            
            .trend-icon {
                margin-right: 5px;
            }
            
            /* Status indicators */
            .status-pending {
                color: #ffb84d;
                font-weight: 600;
            }
            
            .status-processed {
                color: #34d578;
                font-weight: 600;
            }
            
            hr {
                background: linear-gradient(90deg, transparent, rgba(100, 100, 100, 0.5), transparent);
            }
            
            /* Tables */
            .dataframe {
                border-collapse: collapse;
                width: 100%;
                border-radius: 8px;
                overflow: hidden;
            }
            
            .dataframe th {
                background-color: rgba(60, 90, 150, 0.2);
                padding: 12px 15px;
                text-align: left;
                font-weight: 500;
            }
            
            .dataframe td {
                padding: 10px 15px;
                border-top: 1px solid rgba(70, 70, 70, 0.2);
            }
            
            .dataframe tr:nth-child(even) {
                background-color: rgba(50, 55, 65, 0.3);
            }
            
            .stFileUploader {
                background-color: rgba(60, 65, 85, 0.2);
                border: 1px dashed rgba(100, 120, 200, 0.3);
            }
            
            button[kind="primary"] {
                background-color: rgba(100, 150, 255, 0.7);
            }
            
            button[kind="primary"]:hover {
                background-color: rgba(100, 150, 255, 0.9);
            }
            
            /* Additional dark mode styles for other elements */
            .stSlider [data-baseweb=slider] {
                background-color: rgba(60, 65, 85, 0.3);
            }
            
            .stAlert {
                background-color: rgba(30, 34, 44, 0.5);
                border-color: rgba(70, 70, 70, 0.3);
            }
            
            .stSelectbox [data-baseweb=select] div {
                background-color: rgba(30, 34, 44, 0.5);
            }
            
            /* Sidebar styling */
            div[data-testid="stSidebar"] {
                background-color: rgba(17, 20, 28, 0.7);
                border-right: 1px solid rgba(60, 65, 85, 0.3);
            }
            
            /* Date input styling for dark theme */
            div[data-baseweb="calendar"] {
                background-color: rgba(30, 34, 44, 0.95);
                border-color: rgba(80, 100, 180, 0.3);
            }
            
            div[data-baseweb="calendar"] button {
                color: rgba(255, 255, 255, 0.8);
            }
            
            div[data-baseweb="calendar"] button:hover {
                background-color: rgba(80, 120, 230, 0.3);
            }
            
            div[data-baseweb="calendar"] button[aria-selected="true"] {
                background-color: rgba(80, 120, 230, 0.5);
                color: white;
            }
        """

        # Always return dark theme CSS
        return f"""
        <style>
            {base_css}
            {dark_css}
        </style>
        """

    @staticmethod
    def apply_theme(theme="dark"):
        """
        Apply the theme to the Streamlit app.
        Now always applies dark theme regardless of parameter.

        Parameters:
        -----------
        theme : str
            Parameter kept for compatibility but ignored as we always use dark theme
        """
        css = DashboardStyle.get_theme_css()
        st.markdown(css, unsafe_allow_html=True)

    @staticmethod
    def init_theme_selector():
        """
        Initialize a theme selector in the sidebar and apply the selected theme.
        Returns the selected theme.
        """
        # Always apply dark theme - no selector needed
        selected_theme = "dark"
        DashboardStyle.apply_theme(selected_theme)

        # Store the theme choice in the session state
        if "theme" not in st.session_state:
            st.session_state.theme = selected_theme

        return selected_theme

    @staticmethod
    def calendar_icon():
        """Return a calendar SVG icon for date selector"""
        return """
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
        </svg>
        """
