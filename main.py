import calendar
import io
import re
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dateutil.relativedelta import relativedelta

from src.data.parse import get_date_range, process_data

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
        # Load the data
        try:
            df = pd.read_csv(uploaded_file)

            # Process the data
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
                st.header("Work Analytics Overview")

                # Get date range for the data
                min_date, max_date = get_date_range(df)
                st.subheader(
                    f"Data Range: {min_date.strftime('%b %d, %Y')} to {max_date.strftime('%b %d, %Y')}"
                )

                # Date range filter
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", min_date)
                with col2:
                    end_date = st.date_input("End Date", max_date)

                # Apply date filter
                filtered_df = df[
                    (df["workDate_dt"].dt.date >= start_date)
                    & (df["workDate_dt"].dt.date <= end_date)
                ]

                # Top metrics
                total_hours = filtered_df["duration_seconds"].sum() / 3600
                total_earnings = filtered_df["payout_amount"].sum()
                avg_hourly_rate = total_earnings / total_hours if total_hours > 0 else 0
                total_tasks = filtered_df["itemID"].nunique()
                active_days = filtered_df["workDate"].nunique()

                # Display key metrics in columns
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Total Hours</div>'
                        f'<div class="metric-value">{total_hours:.2f}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Total Earnings</div>'
                        f'<div class="metric-value">${total_earnings:.2f}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                with col3:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Avg. Hourly Rate</div>'
                        f'<div class="metric-value">${avg_hourly_rate:.2f}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                with col4:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Total Tasks</div>'
                        f'<div class="metric-value">{total_tasks}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                with col5:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Active Days</div>'
                        f'<div class="metric-value">{active_days}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("<hr>", unsafe_allow_html=True)

                # Trend charts
                st.subheader("Work Trends")

                # Create daily aggregated data with missing dates filled
                daily_data = (
                    filtered_df.groupby("date")
                    .agg({"duration_seconds": "sum", "payout_amount": "sum"})
                    .reset_index()
                )

                # Ensure all dates are included (even non-working days)
                date_range = pd.date_range(start=start_date, end=end_date)
                date_df = pd.DataFrame({"date": date_range})
                # Convert date_df's date column to the same type as daily_hours' date column
                date_df["date"] = date_df["date"].dt.date

                daily_data = pd.merge(date_df, daily_data, on="date", how="left")
                daily_data.fillna(0, inplace=True)

                # Convert seconds to hours
                daily_data["hours"] = daily_data["duration_seconds"] / 3600

                # Create the main trends chart
                col1, col2 = st.columns(2)

                with col1:
                    # Hours trend
                    fig = px.bar(
                        daily_data,
                        x="date",
                        y="hours",
                        title="Daily Working Hours",
                        labels={"date": "Date", "hours": "Hours"},
                        color_discrete_sequence=["#4e8df5"],
                    )

                    # Add a moving average line
                    if len(daily_data) > 3:
                        daily_data["hours_ma"] = (
                            daily_data["hours"].rolling(window=3).mean()
                        )
                        fig.add_scatter(
                            x=daily_data["date"],
                            y=daily_data["hours_ma"],
                            mode="lines",
                            name="3-Day Moving Average",
                            line=dict(width=3, color="red"),
                        )

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Earnings trend
                    fig = px.bar(
                        daily_data,
                        x="date",
                        y="payout_amount",
                        title="Daily Earnings",
                        labels={"date": "Date", "payout_amount": "Earnings ($)"},
                        color_discrete_sequence=["#4CAF50"],
                    )

                    # Add a moving average line
                    if len(daily_data) > 3:
                        daily_data["earnings_ma"] = (
                            daily_data["payout_amount"].rolling(window=3).mean()
                        )
                        fig.add_scatter(
                            x=daily_data["date"],
                            y=daily_data["earnings_ma"],
                            mode="lines",
                            name="3-Day Moving Average",
                            line=dict(width=3, color="red"),
                        )

                    st.plotly_chart(fig, use_container_width=True)

                # Pay type breakdown
                st.subheader("Payment Type Breakdown")

                pay_type_data = (
                    filtered_df.groupby("payType")
                    .agg({"payout_amount": "sum"})
                    .reset_index()
                )

                fig = px.pie(
                    pay_type_data,
                    values="payout_amount",
                    names="payType",
                    title="Earnings by Payment Type",
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                fig.update_traces(textposition="inside", textinfo="percent+label+value")
                fig.update_layout(uniformtext_minsize=12, uniformtext_mode="hide")

                st.plotly_chart(fig, use_container_width=True)

                # Status breakdown
                st.subheader("Payment Status")

                status_data = (
                    filtered_df.groupby("status")
                    .agg({"payout_amount": "sum"})
                    .reset_index()
                )

                col1, col2 = st.columns([2, 3])

                with col1:
                    fig = px.pie(
                        status_data,
                        values="payout_amount",
                        names="status",
                        title="Earnings by Status",
                        color_discrete_map={
                            "pending": "#FFA500",
                            "processed": "#008000",
                        },
                    )
                    fig.update_traces(textposition="inside", textinfo="percent+label")

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Table with pending vs processed
                    st.markdown("#### Payment Status Summary")

                    pending_amount = (
                        status_data[status_data["status"] == "pending"][
                            "payout_amount"
                        ].sum()
                        if "pending" in status_data["status"].values
                        else 0
                    )
                    processed_amount = (
                        status_data[status_data["status"] == "processed"][
                            "payout_amount"
                        ].sum()
                        if "processed" in status_data["status"].values
                        else 0
                    )

                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
                            <div style="text-align: center; padding: 20px; background-color: #fff9e6; border-radius: 10px; width: 45%;">
                                <h3 style="margin: 0; color: #FFA500;">Pending</h3>
                                <p style="font-size: 24px; margin-top: 10px; font-weight: bold;">${pending_amount:.2f}</p>
                            </div>
                            <div style="text-align: center; padding: 20px; background-color: #e6ffe6; border-radius: 10px; width: 45%;">
                                <h3 style="margin: 0; color: #008000;">Processed</h3>
                                <p style="font-size: 24px; margin-top: 10px; font-weight: bold;">${processed_amount:.2f}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Tab 2: Hours Analysis
            with tabs[1]:
                st.header("Working Hours Analysis")

                # Daily hours distribution
                st.subheader("Daily Hours Distribution")

                # Aggregate hours by day
                daily_hours = (
                    filtered_df.groupby("date")
                    .agg({"duration_seconds": "sum"})
                    .reset_index()
                )

                # Ensure all dates are included
                date_range = pd.date_range(start=start_date, end=end_date)
                date_df = pd.DataFrame({"date": date_range})

                # Convert both dataframes to have dates in the same format
                date_df["date"] = date_df["date"].apply(lambda x: x.date())

                # Make sure daily_hours dates are also date objects
                if not isinstance(
                    daily_hours["date"].iloc[0], type(date_df["date"].iloc[0])
                ):
                    daily_hours["date"] = pd.to_datetime(daily_hours["date"]).dt.date

                # Now the merge should work
                daily_hours = pd.merge(date_df, daily_hours, on="date", how="left")
                daily_hours.fillna(0, inplace=True)

                # Convert seconds to hours
                daily_hours["hours"] = daily_hours["duration_seconds"] / 3600

                # Calculate statistics
                avg_hours = daily_hours["hours"].mean()
                max_hours = daily_hours["hours"].max()
                min_hours = (
                    daily_hours[daily_hours["hours"] > 0]["hours"].min()
                    if any(daily_hours["hours"] > 0)
                    else 0
                )
                median_hours = daily_hours["hours"].median()

                # Display statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Average Hours per Day</div>'
                        f'<div class="metric-value">{avg_hours:.2f}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Maximum Hours per Day</div>'
                        f'<div class="metric-value">{max_hours:.2f}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                with col3:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Minimum Hours (Active Days)</div>'
                        f'<div class="metric-value">{min_hours:.2f}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )
                with col4:
                    st.markdown(
                        '<div class="metric-card">'
                        '<div class="metric-title">Median Hours per Day</div>'
                        f'<div class="metric-value">{median_hours:.2f}</div>'
                        "</div>",
                        unsafe_allow_html=True,
                    )

                # Hours histogram
                fig = px.histogram(
                    daily_hours[daily_hours["hours"] > 0],  # Only include active days
                    x="hours",
                    nbins=10,
                    title="Distribution of Daily Hours (Active Days Only)",
                    labels={"hours": "Hours Worked"},
                    color_discrete_sequence=["#4e8df5"],
                )

                # Add a vertical line for the average
                fig.add_vline(
                    x=avg_hours,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Avg: {avg_hours:.2f}h",
                    annotation_position="top right",
                )

                st.plotly_chart(fig, use_container_width=True)

                # Hours by day of week
                st.subheader("Working Hours by Day of Week")

                # Add day of week to daily hours

                daily_hours["date"] = pd.to_datetime(daily_hours["date"])
                daily_hours["day_of_week"] = daily_hours["date"].dt.day_name()

                # Aggregate by day of week
                day_of_week_hours = (
                    daily_hours.groupby("day_of_week")
                    .agg({"hours": "sum"})
                    .reset_index()
                )

                # Ensure proper ordering of days
                days_order = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                day_of_week_hours["day_of_week"] = pd.Categorical(
                    day_of_week_hours["day_of_week"],
                    categories=days_order,
                    ordered=True,
                )
                day_of_week_hours = day_of_week_hours.sort_values("day_of_week")

                fig = px.bar(
                    day_of_week_hours,
                    x="day_of_week",
                    y="hours",
                    title="Total Hours by Day of Week",
                    labels={"day_of_week": "Day of Week", "hours": "Total Hours"},
                    color_discrete_sequence=["#4e8df5"],
                )

                st.plotly_chart(fig, use_container_width=True)

                # Regular vs Overtime hours
                st.subheader("Regular vs. Overtime Hours")

                # Group by date and payment type
                overtime_data = (
                    filtered_df.groupby(["date", "is_overtime"])
                    .agg({"duration_seconds": "sum"})
                    .reset_index()
                )

                # Convert to hours
                overtime_data["hours"] = overtime_data["duration_seconds"] / 3600

                # Pivot the data to have regular and overtime hours as columns
                overtime_pivot = overtime_data.pivot_table(
                    index="date", columns="is_overtime", values="hours", fill_value=0
                ).reset_index()

                # Rename columns
                overtime_pivot.columns.name = None
                if True in overtime_pivot.columns:
                    overtime_pivot.rename(
                        columns={True: "Overtime Hours"}, inplace=True
                    )
                else:
                    overtime_pivot["Overtime Hours"] = 0

                if False in overtime_pivot.columns:
                    overtime_pivot.rename(
                        columns={False: "Regular Hours"}, inplace=True
                    )
                else:
                    overtime_pivot["Regular Hours"] = 0

                # Ensure the date column is properly named
                if "date" not in overtime_pivot.columns:
                    overtime_pivot.rename(
                        columns={overtime_pivot.columns[0]: "date"}, inplace=True
                    )

                # Create a stacked bar chart
                fig = go.Figure()

                fig.add_trace(
                    go.Bar(
                        x=overtime_pivot["date"],
                        y=(
                            overtime_pivot["Regular Hours"]
                            if "Regular Hours" in overtime_pivot.columns
                            else 0
                        ),
                        name="Regular Hours",
                        marker_color="#4e8df5",
                    )
                )

                fig.add_trace(
                    go.Bar(
                        x=overtime_pivot["date"],
                        y=(
                            overtime_pivot["Overtime Hours"]
                            if "Overtime Hours" in overtime_pivot.columns
                            else 0
                        ),
                        name="Overtime Hours",
                        marker_color="#FFA500",
                    )
                )

                fig.update_layout(
                    title="Regular vs. Overtime Hours by Day",
                    xaxis_title="Date",
                    yaxis_title="Hours",
                    barmode="stack",
                )

                st.plotly_chart(fig, use_container_width=True)

                # Monthly hour totals
                st.subheader("Monthly Hours Summary")

                daily_hours["date"] = pd.to_datetime(daily_hours["date"])

                # Now add the weekday and week number
                daily_hours["weekday"] = daily_hours["date"].dt.day_name()
                daily_hours["week_num"] = daily_hours["date"].dt.isocalendar().week

                # Add month to daily hours
                daily_hours["month"] = daily_hours["date"].dt.strftime("%b %Y")

                # Aggregate by month
                monthly_hours = (
                    daily_hours.groupby("month").agg({"hours": "sum"}).reset_index()
                )

                # Sort by date
                monthly_hours["sort_date"] = pd.to_datetime(
                    monthly_hours["month"], format="%b %Y"
                )
                monthly_hours.sort_values("sort_date", inplace=True)

                fig = px.bar(
                    monthly_hours,
                    x="month",
                    y="hours",
                    title="Total Hours by Month",
                    labels={"month": "Month", "hours": "Total Hours"},
                    color_discrete_sequence=["#4e8df5"],
                )

                st.plotly_chart(fig, use_container_width=True)

                # Hours heatmap by week day
                st.subheader("Working Hours Heatmap")
                daily_hours["date"] = pd.to_datetime(daily_hours["date"])

                # Create a heatmap dataframe
                daily_hours["weekday"] = daily_hours["date"].dt.day_name()
                daily_hours["week_num"] = daily_hours["date"].dt.isocalendar().week

                # Pivot the data for the heatmap
                heatmap_data = daily_hours.pivot_table(
                    index="weekday", columns="week_num", values="hours", fill_value=0
                )

                # Ensure proper ordering of days
                heatmap_data = heatmap_data.reindex(days_order)

                # Create heatmap
                fig = px.imshow(
                    heatmap_data,
                    labels=dict(x="Week Number", y="Day of Week", color="Hours"),
                    x=heatmap_data.columns,
                    y=heatmap_data.index,
                    aspect="auto",
                    color_continuous_scale="Blues",
                )

                fig.update_layout(
                    title="Working Hours Heatmap (Week × Day)",
                    xaxis_title="Week Number",
                    yaxis_title="Day of Week",
                )

                st.plotly_chart(fig, use_container_width=True)

            # Tab 3: Earnings Analysis
            with tabs[2]:
                st.header("Earnings Analysis")

                # Daily earnings
                st.subheader("Daily Earnings Breakdown")

                # Aggregate earnings by day and payment type
                daily_earnings = (
                    filtered_df.groupby(["date", "payType"])
                    .agg({"payout_amount": "sum"})
                    .reset_index()
                )

                # Pivot the data to have payment types as columns
                earnings_pivot = daily_earnings.pivot_table(
                    index="date",
                    columns="payType",
                    values="payout_amount",
                    fill_value=0,
                ).reset_index()

                # Ensure all payTypes are included as columns
                pay_types = filtered_df["payType"].unique()
                for pay_type in pay_types:
                    if pay_type not in earnings_pivot.columns:
                        earnings_pivot[pay_type] = 0

                # Create a stacked bar chart
                fig = go.Figure()

                colors = {
                    "prepay": "#4CAF50",
                    "overtimePay": "#FFA500",
                    "payAdjustment": "#F44336",
                    "missionReward": "#9C27B0",
                }

                for pay_type in pay_types:
                    if pay_type in earnings_pivot.columns:
                        fig.add_trace(
                            go.Bar(
                                x=earnings_pivot["date"],
                                y=earnings_pivot[pay_type],
                                name=pay_type,
                                marker_color=colors.get(pay_type, "#4e8df5"),
                            )
                        )

                fig.update_layout(
                    title="Daily Earnings by Payment Type",
                    xaxis_title="Date",
                    yaxis_title="Earnings ($)",
                    barmode="stack",
                )

                st.plotly_chart(fig, use_container_width=True)

                # Payment type summary
                st.subheader("Payment Type Summary")

                pay_type_summary = (
                    filtered_df.groupby("payType")
                    .agg({"payout_amount": "sum", "itemID": "count"})
                    .reset_index()
                )

                pay_type_summary.rename(
                    columns={
                        "payout_amount": "Total Amount",
                        "itemID": "Number of Entries",
                    },
                    inplace=True,
                )

                col1, col2 = st.columns(2)

                with col1:
                    fig = px.pie(
                        pay_type_summary,
                        values="Total Amount",
                        names="payType",
                        title="Earnings by Payment Type",
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                    )
                    fig.update_traces(textposition="inside", textinfo="percent+label")

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = px.bar(
                        pay_type_summary,
                        x="payType",
                        y="Total Amount",
                        title="Total Earnings by Payment Type",
                        labels={
                            "payType": "Payment Type",
                            "Total Amount": "Total Earnings ($)",
                        },
                        color="payType",
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                    )

                    fig.update_layout(showlegend=False)

                    st.plotly_chart(fig, use_container_width=True)

                # Hourly rate analysis
                st.subheader("Hourly Rate Analysis")

                # Get unique hourly rates
                hourly_rates = filtered_df[filtered_df["hourly_rate"] > 0][
                    "hourly_rate"
                ].unique()

                # Aggregate earnings by hourly rate
                rate_earnings = (
                    filtered_df[filtered_df["hourly_rate"] > 0]
                    .groupby("hourly_rate")
                    .agg({"payout_amount": "sum", "duration_seconds": "sum"})
                    .reset_index()
                )

                # Calculate effective rate
                rate_earnings["effective_rate"] = rate_earnings["payout_amount"] / (
                    rate_earnings["duration_seconds"] / 3600
                )

                # Calculate hours
                rate_earnings["hours"] = rate_earnings["duration_seconds"] / 3600

                col1, col2 = st.columns(2)

                with col1:
                    fig = px.bar(
                        rate_earnings,
                        x="hourly_rate",
                        y="payout_amount",
                        title="Earnings by Hourly Rate",
                        labels={
                            "hourly_rate": "Hourly Rate ($)",
                            "payout_amount": "Total Earnings ($)",
                        },
                        color="hourly_rate",
                        color_continuous_scale="Viridis",
                    )

                    fig.update_layout(showlegend=False)

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = px.bar(
                        rate_earnings,
                        x="hourly_rate",
                        y="hours",
                        title="Hours Worked by Hourly Rate",
                        labels={
                            "hourly_rate": "Hourly Rate ($)",
                            "hours": "Hours Worked",
                        },
                        color="hourly_rate",
                        color_continuous_scale="Viridis",
                    )

                    fig.update_layout(showlegend=False)

                    st.plotly_chart(fig, use_container_width=True)

                # Monthly earnings trend
                st.subheader("Monthly Earnings Trend")

                # Aggregate earnings by month
                monthly_earnings = (
                    filtered_df.groupby(filtered_df["workDate_dt"].dt.strftime("%b %Y"))
                    .agg({"payout_amount": "sum"})
                    .reset_index()
                )

                # Sort by date
                monthly_earnings["sort_date"] = pd.to_datetime(
                    monthly_earnings["workDate_dt"], format="%b %Y"
                )
                monthly_earnings.sort_values("sort_date", inplace=True)

                fig = px.line(
                    monthly_earnings,
                    x="workDate_dt",
                    y="payout_amount",
                    title="Monthly Earnings Trend",
                    labels={
                        "workDate_dt": "Month",
                        "payout_amount": "Total Earnings ($)",
                    },
                    markers=True,
                )

                st.plotly_chart(fig, use_container_width=True)

                # Earnings distribution
                st.subheader("Daily Earnings Distribution")

                daily_earnings = (
                    filtered_df.groupby("date")
                    .agg({"payout_amount": "sum"})
                    .reset_index()
                )

                fig = px.histogram(
                    daily_earnings[daily_earnings["payout_amount"] > 0],
                    x="payout_amount",
                    nbins=20,
                    title="Distribution of Daily Earnings (Active Days Only)",
                    labels={"payout_amount": "Daily Earnings ($)"},
                    color_discrete_sequence=["#4CAF50"],
                )

                # Add mean line
                mean_earnings = daily_earnings[daily_earnings["payout_amount"] > 0][
                    "payout_amount"
                ].mean()
                fig.add_vline(
                    x=mean_earnings,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Avg: ${mean_earnings:.2f}",
                    annotation_position="top right",
                )

                st.plotly_chart(fig, use_container_width=True)

            # Tab 4: Project & Task Details
            with tabs[3]:
                st.header("Project and Task Analysis")

                # Project breakdown
                st.subheader("Project Distribution")

                project_summary = (
                    filtered_df.groupby("projectName")
                    .agg(
                        {
                            "payout_amount": "sum",
                            "duration_seconds": "sum",
                            "itemID": "count",
                        }
                    )
                    .reset_index()
                )

                project_summary["hours"] = project_summary["duration_seconds"] / 3600
                project_summary["effective_rate"] = (
                    project_summary["payout_amount"] / project_summary["hours"]
                )

                col1, col2 = st.columns(2)

                with col1:
                    fig = px.pie(
                        project_summary,
                        values="payout_amount",
                        names="projectName",
                        title="Earnings by Project",
                    )
                    fig.update_traces(textposition="inside", textinfo="percent+label")

                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = px.pie(
                        project_summary,
                        values="hours",
                        names="projectName",
                        title="Hours by Project",
                    )
                    fig.update_traces(textposition="inside", textinfo="percent+label")

                    st.plotly_chart(fig, use_container_width=True)

                # Project details table
                st.subheader("Project Details")

                project_table = project_summary.copy()
                project_table["payout_amount"] = project_table["payout_amount"].round(2)
                project_table["hours"] = project_table["hours"].round(2)
                project_table["effective_rate"] = project_table["effective_rate"].round(
                    2
                )

                project_table.columns = [
                    "Project Name",
                    "Total Earnings ($)",
                    "Duration (s)",
                    "Number of Tasks",
                    "Hours Worked",
                    "Effective Rate ($/hr)",
                ]

                st.dataframe(
                    project_table.drop("Duration (s)", axis=1), use_container_width=True
                )

                # Task completion timeline
                st.subheader("Task Completion Timeline")

                task_timeline = filtered_df.copy()
                task_timeline["completion_date"] = pd.to_datetime(
                    task_timeline["workDate"]
                )

                fig = px.scatter(
                    task_timeline,
                    x="completion_date",
                    y="projectName",
                    size="payout_amount",
                    color="payType",
                    title="Task Completion Timeline",
                    labels={
                        "completion_date": "Completion Date",
                        "projectName": "Project",
                        "payout_amount": "Earnings ($)",
                    },
                )

                st.plotly_chart(fig, use_container_width=True)

            # Tab 5: Calendar View
            with tabs[4]:
                st.header("Calendar View")

                # Get the current month and year
                today = datetime.now()

                # Create month selection
                # Include the current month and previous months
                months = pd.date_range(
                    start=min_date, end=today + relativedelta(months=1), freq="M"
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
                month_data = filtered_df[
                    (filtered_df["workDate_dt"].dt.year == selected_date.year)
                    & (filtered_df["workDate_dt"].dt.month == selected_date.month)
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
                                day_data = daily_summary[
                                    daily_summary["workDate_dt"] == day
                                ]
                                hours = (
                                    day_data["hours"].iloc[0]
                                    if not day_data.empty
                                    else 0
                                )
                                earnings = (
                                    day_data["payout_amount"].iloc[0]
                                    if not day_data.empty
                                    else 0
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

            # Tab 6: Raw Data
            with tabs[5]:
                st.header("Raw Data")

                # Add search functionality
                search_term = st.text_input("Search in data:", "")

                # Filter data based on search term
                if search_term:
                    filtered_display_df = filtered_df[
                        filtered_df.astype(str)
                        .apply(lambda x: x.str.contains(search_term, case=False))
                        .any(axis=1)
                    ]
                else:
                    filtered_display_df = filtered_df

                # Display data
                st.dataframe(filtered_display_df, use_container_width=True)

                # Add download button
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="work_data.csv",
                    mime="text/csv",
                )

        except Exception as e:
            st.error(f"Error processing the file: {str(e)}")
            st.write("Please make sure the uploaded file is in the correct format.")


if __name__ == "__main__":
    main()
