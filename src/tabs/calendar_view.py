import calendar
from datetime import datetime

import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

from src.data.parse import get_date_range
from src.utils.styling import DashboardStyle


def calendar_view_tab(df):
    start_date, _ = get_date_range(df)

    # Use a container for better layout control
    with st.container():
        # Title with improved styling
        st.markdown(
            """
        <div style="display: flex; align-items: center; margin-bottom: 25px; border-bottom: 1px solid rgba(100, 120, 200, 0.2); padding-bottom: 10px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="#5e9df5" viewBox="0 0 16 16" style="margin-right: 10px;">
                <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM1 4v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V4H1z"/>
            </svg>
            <h1 style="margin: 0; font-size: 1.8rem; font-weight: 600; background: linear-gradient(90deg, #5e9df5, #9c6cf5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Calendar View</h1>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Get the current month and year
    today = datetime.now()

    # Create month selection
    # Include the current month and previous months
    months = pd.date_range(
        start=start_date, end=today + relativedelta(months=1), freq="M"
    )
    month_options = [d.strftime("%B %Y") for d in months]

    selected_month = st.selectbox(
        "",
        options=month_options,
        index=len(month_options) - 1,
        label_visibility="collapsed",
    )

    # Parse selected month
    selected_date = datetime.strptime(selected_month, "%B %Y")
    cal = calendar.monthcalendar(selected_date.year, selected_date.month)

    # Prepare daily data for the selected month
    month_data = df[
        (df["workDate_dt"].dt.year == selected_date.year)
        & (df["workDate_dt"].dt.month == selected_date.month)
    ]

    # Group by day of month
    daily_summary = (
        month_data.groupby(month_data["workDate_dt"].dt.day)
        .agg({"duration_seconds": "sum", "payout_amount": "sum"})
        .reset_index()
    )

    # Convert seconds to hours
    daily_summary["hours"] = daily_summary["duration_seconds"] / 3600

    # Create month title with modern design
    st.markdown(
        f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid rgba(100, 120, 200, 0.2);
    ">
        <h2 style="
            margin: 0;
            font-weight: 600;
            font-size: 1.6rem;
            color: #e6e6e6;
            letter-spacing: 0.03em;
        ">{selected_date.strftime('%B %Y')}</h2>
        <div style="
            background: rgba(80, 120, 230, 0.2);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.8);
        ">
            {len(daily_summary[daily_summary["hours"] > 0])} active days
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Create header row with improved styling
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Use a single HTML component for the day headers for better alignment
    day_headers_html = '<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 3px;">'

    for day in days:
        day_headers_html += f"""
            <div style="
                text-align: center;
                font-weight: 600;
                font-size: 0.95rem;
                padding: 6px 0;
                background-color: rgba(60, 90, 150, 0.25);
                border-radius: 8px;
                color: rgba(255, 255, 255, 0.9);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            ">
                {day}
            </div>
        """

    day_headers_html += "</div>"

    st.components.v1.html(day_headers_html, height=45)  # Reduced height from 60 to 45

    # Create calendar grid with CSS Grid for better alignment
    for week in cal:
        # Create a single grid for the entire week
        week_html = '<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 0px;">'

        for day in week:
            if day != 0:
                # Find data for this day
                day_data = daily_summary[daily_summary["workDate_dt"] == day]
                hours = day_data["hours"].iloc[0] if not day_data.empty else 0
                earnings = (
                    day_data["payout_amount"].iloc[0] if not day_data.empty else 0
                )

                # Determine styling based on hours worked
                if hours > 0:
                    bg_color = "rgba(80, 120, 230, 0.2)"
                    border_color = "rgba(100, 150, 255, 0.4)"
                    shadow = "0 4px 12px rgba(0, 0, 0, 0.15)"
                else:
                    bg_color = "rgba(30, 34, 44, 0.5)"
                    border_color = "rgba(70, 70, 70, 0.3)"
                    shadow = "0 2px 8px rgba(0, 0, 0, 0.1)"

                week_html += f"""
                <div style="
                    border: 1px solid {border_color};
                    padding: 8px;
                    border-radius: 10px;
                    background-color: {bg_color};
                    min-height: 90px;
                    box-shadow: {shadow};
                    transition: all 0.3s ease;
                    cursor: default;
                    display: flex;
                    flex-direction: column;
                "
                onmouseover="this.style.boxShadow='0 8px 20px rgba(0, 0, 0, 0.25)'; this.style.transform='translateY(-2px)';"
                onmouseout="this.style.boxShadow='{shadow}'; this.style.transform='translateY(0)';"
                >
                    <div style="
                        font-weight: 600;
                        font-size: 1.1em;
                        padding: 2px 6px;
                        background-color: rgba(40, 50, 70, 0.4);
                        border-radius: 6px;
                        color: rgba(255, 255, 255, 0.9);
                        text-align: center;
                        margin-bottom: 8px;
                    ">{day}</div>
                    
                    <div style="
                        display: flex;
                        flex-direction: column;
                        gap: 4px;
                        margin-top: auto;
                    ">
                        <div style="
                            color: #5e9df5;
                            font-size: 1em;
                            font-weight: 500;
                            text-align: center;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16" style="margin-right: 3px;">
                                <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                                <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
                            </svg>
                            {hours:.1f}h
                        </div>
                        
                        <div style="
                            background: linear-gradient(90deg, #34d578, #2bb573);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            font-weight: 600;
                            font-size: 0.95em;
                            text-align: center;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        ">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="#34d578" viewBox="0 0 16 16" style="margin-right: 3px;">
                                <path d="M4 10.781c.148 1.667 1.513 2.85 3.591 3.003V15h1.043v-1.216c2.27-.179 3.678-1.438 3.678-3.3 0-1.59-.947-2.51-2.956-3.028l-.722-.187V3.467c1.122.11 1.879.714 2.07 1.616h1.47c-.166-1.6-1.54-2.748-3.54-2.875V1H7.591v1.233c-1.939.23-3.27 1.472-3.27 3.156 0 1.454.966 2.483 2.661 2.917l.61.162v4.031c-1.149-.17-1.94-.8-2.131-1.718H4zm3.391-3.836c-1.043-.263-1.6-.825-1.6-1.616 0-.944.704-1.641 1.8-1.828v3.495l-.2-.05zm1.591 1.872c1.287.323 1.852.859 1.852 1.769 0 1.097-.826 1.828-2.2 1.939V8.73l.348.086z"/>
                            </svg>
                            ${earnings:.2f}
                        </div>
                    </div>
                </div>
                """
            else:
                # Empty cell for days not in this month - styled to match
                week_html += """
                <div style="
                    border: 1px solid rgba(50, 50, 50, 0.2);
                    padding: 8px;
                    border-radius: 10px;
                    background-color: rgba(20, 25, 35, 0.3);
                    min-height: 90px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                ">
                </div>
                """

        week_html += "</div>"

        # Render the entire week grid as one component
        st.components.v1.html(week_html, height=120)  # Reduced height from 180 to 120

    # Close the calendar container
    st.markdown("</div>", unsafe_allow_html=True)

    # Monthly summary with enhanced styling
    st.markdown(
        """
    <div style="
        background: linear-gradient(90deg, rgba(30, 34, 44, 0.3) 0%, rgba(30, 34, 44, 0.15) 100%);
        padding: 25px;
        border-radius: 14px;
        margin: 8px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(80, 100, 180, 0.15);
    ">
        <div style="
            display: flex;
            align-items: center;
            border-bottom: 1px solid rgba(100, 120, 200, 0.2);
        ">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="#5e9df5" viewBox="0 0 16 16" style="margin-right: 10px;">
                <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zm-8-3a1 1 0 0 0-.867.5 1 1 0 1 1-1.731-1A3 3 0 0 1 13 8a3.001 3.001 0 0 1-2 2.83V11a1 1 0 1 1-2 0v-1a1 1 0 0 1 1-1 1 1 0 1 0 1-1 1 1 0 0 0-1-1 1 1 0 0 1-1-1 1 1 0 1 1 2 0 1 1 0 0 0 1 1 1 1 0 0 0 1-1 1 1 0 0 0-1-1 3 3 0 0 1-3-3 3 3 0 0 1 6 0 1 1 0 1 1-2 0 1 1 0 0 0-1-1 1 1 0 0 0-1 1v.17a1 1 0 0 1-2 0V4.83A1 1 0 0 1 7.93 4a1 1 0 0 0 0-2 3 3 0 0 1-3.2 3c-.02 0-.03.01-.05.01A1 1 0 1 1 4 3.5c.03-.02.05-.03.08-.04.03-.01.05-.02.07-.04.01-.01.02-.01.03-.02A1 1 0 1 0 5 2a1 1 0 0 1 0-2 3 3 0 0 1 3 3c0 .11-.01.21-.02.31a1 1 0 0 1-.38.67 1 1 0 0 0-.38.67c0 .08.02.16.04.24.01.06.03.12.04.19.02.13.06.24.13.34.07.1.15.19.27.26a1 1 0 0 0 .9-1.78c-.02-.02-.04-.02-.06-.04a1 1 0 1 1 .82-1.83 3 3 0 0 1 4.43 2.25A3.002 3.002 0 0 1 15 9a3 3 0 0 1-2.83 2.99A1 1 0 0 1 11 13v1a1 1 0 1 1-2 0v-1a1 1 0 0 1 1-1 1 1 0 0 0 1-1 1 1 0 0 0-1-1 1 1 0 0 1-1-1 1 1 0 1 1 2 0 1 1 0 0 0 1 1 1 1 0 1 0 0-2 3 3 0 0 1-3-3 3.003 3.003 0 0 1 4-2.83V2a1 1 0 0 1 1-1 1 1 0 0 1 1 1v1a1 1 0 0 1-1 1 1 1 0 1 0-1 1 1 1 0 0 0 1 1 1 1 0 0 1 1 1 1 1 0 1 1-2 0 1 1 0 0 0-1-1 1 1 0 0 0-1 1c0 .34.08.67.21.96.09.23.22.44.39.64.09.11.2.21.31.29.11.09.23.17.36.24a1 1 0 0 1-1 1.74z"/>
            </svg>
            <h3 style="
                margin: 0;
                font-size: 1.3rem;
                font-weight: 600;
                color: #e6e6e6;
                letter-spacing: 0.02em;
            ">Monthly Summary</h3>
        </div>
    """,
        unsafe_allow_html=True,
    )

    total_month_hours = daily_summary["hours"].sum()
    total_month_earnings = daily_summary["payout_amount"].sum()
    working_days = len(daily_summary[daily_summary["hours"] > 0])
    avg_daily_hours = total_month_hours / working_days if working_days > 0 else 0
    avg_daily_earnings = total_month_earnings / working_days if working_days > 0 else 0

    # Display summary cards in a grid
    metrics_html = """
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;">
    """

    metrics_data = [
        {
            "title": "Total Hours",
            "value": f"{total_month_hours:.1f}",
            "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
            </svg>""",
        },
        {
            "title": "Total Earnings",
            "value": f"${total_month_earnings:.2f}",
            "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                <path d="M4 10.781c.148 1.667 1.513 2.85 3.591 3.003V15h1.043v-1.216c2.27-.179 3.678-1.438 3.678-3.3 0-1.59-.947-2.51-2.956-3.028l-.722-.187V3.467c1.122.11 1.879.714 2.07 1.616h1.47c-.166-1.6-1.54-2.748-3.54-2.875V1H7.591v1.233c-1.939.23-3.27 1.472-3.27 3.156 0 1.454.966 2.483 2.661 2.917l.61.162v4.031c-1.149-.17-1.94-.8-2.131-1.718H4zm3.391-3.836c-1.043-.263-1.6-.825-1.6-1.616 0-.944.704-1.641 1.8-1.828v3.495l-.2-.05zm1.591 1.872c1.287.323 1.852.859 1.852 1.769 0 1.097-.826 1.828-2.2 1.939V8.73l.348.086z"/>
            </svg>""",
        },
        {
            "title": "Working Days",
            "value": f"{working_days}",
            "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 16 16">
                <path d="M3.5 0a.5.5 0 0 1 .5.5V1h8V.5a.5.5 0 0 1 1 0V1h1a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V3a2 2 0 0 1 2-2h1V.5a.5.5 0 0 1 .5-.5zM2 2a1 1 0 0 0-1 1v1h14V3a1 1 0 0 0-1-1H2zm13 3H1v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V5z"/>
                <path d="M11 7.5a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5v-1z"/>
            </svg>""",
        },
    ]

    for metric in metrics_data:
        metrics_html += f"""
        <div class="metric-card" style="
            background-color: rgba(30, 34, 44, 0.5);
            border: 1px solid rgba(70, 70, 70, 0.3);
            padding: 22px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        "
        onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 25px rgba(0, 0, 0, 0.3)';"
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(0, 0, 0, 0.2)';">
            <div style="
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #bbb;
                opacity: 0.8;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 12px;
            ">
                <span style="margin-right: 6px; color: #5e9df5;">{metric["icon"]}</span>
                {metric["title"]}
            </div>
            <div style="
                font-size: 28px;
                font-weight: 600;
                margin: 12px 0 8px;
                background: linear-gradient(90deg, #5e9df5, #9c6cf5);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">{metric["value"]}</div>
        </div>
        """

    # Add additional metrics row for averages
    metrics_html += """
    </div>
    
    <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(100, 120, 200, 0.1);">
        <h4 style="margin: 0 0 15px 0; font-size: 1.05rem; color: #e6e6e6; font-weight: 500;">Daily Averages</h4>
        
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
    """

    avg_metrics = [
        {
            "title": "Avg. Hours per Day",
            "value": f"{avg_daily_hours:.1f}h",
            "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>""",
        },
        {
            "title": "Avg. Earnings per Day",
            "value": f"${avg_daily_earnings:.2f}",
            "icon": """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 16 16">
                <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>
            </svg>""",
        },
    ]

    for metric in avg_metrics:
        metrics_html += f"""
        <div style="
            background-color: rgba(40, 45, 55, 0.4);
            border: 1px solid rgba(80, 100, 180, 0.15);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div style="
                font-size: 0.9rem;
                color: rgba(255, 255, 255, 0.7);
                display: flex;
                align-items: center;
            ">
                <span style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    background-color: rgba(80, 120, 230, 0.15);
                    margin-right: 10px;
                    color: #5e9df5;
                ">{metric["icon"]}</span>
                {metric["title"]}
            </div>
            <div style="
                font-size: 1.2rem;
                font-weight: 600;
                color: #5e9df5;
            ">{metric["value"]}</div>
        </div>
        """

    metrics_html += """
        </div>
    </div>
    </div>
    """

    st.components.v1.html(metrics_html, height=450)
