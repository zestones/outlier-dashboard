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
