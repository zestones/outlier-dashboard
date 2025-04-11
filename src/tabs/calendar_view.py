import calendar
from datetime import datetime

import pandas as pd
import streamlit as st
from dateutil.relativedelta import relativedelta

from src.data.parse import get_date_range


def calendar_view_tab(df):
    start_date, _ = get_date_range(df)

    st.header("Calendar View")

    # Get the current month and year
    today = datetime.now()

    # Create month selection
    # Include the current month and previous months
    months = pd.date_range(
        start=start_date, end=today + relativedelta(months=1), freq="M"
    )
    month_options = [d.strftime("%B %Y") for d in months]
    selected_month = st.selectbox(
        "Select Month", options=month_options, index=len(month_options) - 1
    )

    # Parse selected month
    selected_date = datetime.strptime(selected_month, "%B %Y")

    # Create calendar data
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

    # Create the calendar layout using st.columns
    st.write(f"### {selected_date.strftime('%B %Y')}")

    # Create header row
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.write(f"**{day}**")

    # Create calendar grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day != 0:
                    # Find data for this day
                    day_data = daily_summary[daily_summary["workDate_dt"] == day]
                    hours = day_data["hours"].iloc[0] if not day_data.empty else 0
                    earnings = (
                        day_data["payout_amount"].iloc[0] if not day_data.empty else 0
                    )

                    # Create a container for the day
                    st.markdown(
                        f"""
                        <div style="
                            border: 1px solid #ddd;
                            padding: 10px;
                            border-radius: 5px;
                            background-color: {'#f8f9fa' if hours > 0 else 'white'};
                            min-height: 100px;
                        ">
                            <div style="font-weight: bold; font-size: 1.2em;">{day}</div>
                            <div style="color: #4e8df5;">{hours:.1f}h</div>
                            <div style="color: #4CAF50;">${earnings:.2f}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    # Empty cell for days not in this month
                    st.markdown(
                        """
                        <div style="
                            border: 1px solid #eee;
                            padding: 10px;
                            border-radius: 5px;
                            background-color: #f8f9fa;
                            min-height: 100px;
                        ">
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Add some spacing
    st.write("")

    # Monthly summary
    st.subheader("Monthly Summary")

    total_month_hours = daily_summary["hours"].sum()
    total_month_earnings = daily_summary["payout_amount"].sum()
    working_days = len(daily_summary[daily_summary["hours"] > 0])

    # Display summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Hours", f"{total_month_hours:.1f}")

    with col2:
        st.metric("Total Earnings", f"${total_month_earnings:.2f}")

    with col3:
        st.metric("Working Days", working_days)
