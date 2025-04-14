import calendar
import datetime as dt
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.data.parse import get_date_range


def display_overview_tab(df):
    """Main function to display the enhanced overview tab."""

    # Add date selector with presets for better UX
    filtered_df = enhanced_date_selector(df)

    # ---- SECTION 1: KPI Metrics ----
    display_enhanced_kpi_metrics(df, filtered_df)

    # ---- SECTION 2: Performance Trends ----
    display_performance_trends(filtered_df)

    # ---- SECTION 3: Earnings Breakdown ----
    display_enhanced_payment_breakdowns(filtered_df)


def enhanced_date_selector(df):
    """Enhanced date selector with modern design and quick presets."""
    min_date, max_date = get_date_range(df)

    # Initialize session state for date inputs
    if "start_date" not in st.session_state:
        st.session_state["start_date"] = min_date
    if "end_date" not in st.session_state:
        st.session_state["end_date"] = max_date

    # Create a clean layout for preset buttons
    preset_container = st.container()
    preset_container.markdown(
        "<p style='margin-bottom: 8px; font-size: 0.9rem; color: #b0b0b0;'>Quick Presets</p>",
        unsafe_allow_html=True,
    )

    # Create modern button styling
    button_style = """
    <style>
        div[data-testid="stHorizontalBlock"] button {
            background-color: rgba(79, 134, 247, 0.1);
            border: 1px solid rgba(79, 134, 247, 0.3);
            color: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            transition: all 0.2s ease;
            box-shadow: none;
            min-height: 36px;
        }
        div[data-testid="stHorizontalBlock"] button:hover {
            background-color: rgba(79, 134, 247, 0.2);
            border-color: rgba(79, 134, 247, 0.6);
            color: white;
        }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    # Button row with better layout
    btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = preset_container.columns(
        [1, 1, 1, 1, 1]
    )

    # Date preset buttons
    if btn_col1.button("Last 7 Days", use_container_width=True):
        end_date = max_date
        start_date = end_date - timedelta(days=6)
        st.session_state["start_date"] = start_date
        st.session_state["end_date"] = end_date

    if btn_col2.button("Last 30 Days", use_container_width=True):
        end_date = max_date
        start_date = end_date - timedelta(days=29)
        st.session_state["start_date"] = start_date
        st.session_state["end_date"] = end_date

    if btn_col3.button("This Month", use_container_width=True):
        end_date = max_date
        start_date = dt.date(end_date.year, end_date.month, 1)
        st.session_state["start_date"] = start_date
        st.session_state["end_date"] = end_date

    if btn_col4.button("Last Month", use_container_width=True):
        current_month = max_date.month
        current_year = max_date.year

        if current_month == 1:
            last_month = 12
            last_month_year = current_year - 1
        else:
            last_month = current_month - 1
            last_month_year = current_year

        last_day = calendar.monthrange(last_month_year, last_month)[1]
        start_date = dt.date(last_month_year, last_month, 1)
        end_date = dt.date(last_month_year, last_month, last_day)
        st.session_state["start_date"] = start_date
        st.session_state["end_date"] = end_date

    if btn_col5.button("All Time", use_container_width=True):
        st.session_state["start_date"] = min_date
        st.session_state["end_date"] = max_date

    # Date input fields with improved styling
    input_container = preset_container.container()
    date_cols = input_container.columns([1, 1])

    # Custom styling for date inputs
    date_input_style = """
    <style>
    div[data-baseweb="calendar"] {
        background-color: rgba(30, 34, 44, 0.9);
        border-radius: 8px;
    }
    div[data-baseweb="input"] {
        background-color: rgba(41, 52, 98, 0.2);
        border-radius: 8px;
    }
    </style>
    """
    st.markdown(date_input_style, unsafe_allow_html=True)

    with date_cols[0]:
        start_date = st.date_input(
            "Start Date", st.session_state["start_date"], key="start_date_input"
        )
        st.session_state["start_date"] = start_date

    with date_cols[1]:
        end_date = st.date_input(
            "End Date", st.session_state["end_date"], key="end_date_input"
        )
        st.session_state["end_date"] = end_date

    # Apply date filter
    filtered_df = df[
        (df["workDate_dt"].dt.date >= start_date)
        & (df["workDate_dt"].dt.date <= end_date)
    ]

    # Show the date range info with improved styling
    total_days = (end_date - start_date).days + 1
    active_days = filtered_df["workDate"].nunique()

    preset_container.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; 
                    padding: 12px 16px; 
                    font-size: 0.9rem; 
                    margin-top: 15px;
                    background-color: rgba(41, 52, 98, 0.1);
                    border-radius: 8px;">
            <div>Selected period: <span style="font-weight: 500; color: #9ab4ff;">{start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')}</span></div>
            <div>Total days: <span style="font-weight: 500; color: #9ab4ff;">{total_days}</span> (Active days: <span style="font-weight: 500; color: #9ab4ff;">{active_days}</span>)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    return filtered_df


def calculate_trend(current_value, previous_value):
    """Calculate the trend percentage change."""
    print(f"Current Value: {current_value}, Previous Value: {previous_value}")
    if previous_value == 0:
        if current_value > 0:
            return 100  # Infinite growth represented as 100%
        return 0

    percentage = ((current_value - previous_value) / previous_value) * 100
    return percentage


def create_kpi_card(title, value, prefix="", unit="", trend=None, tooltip=""):
    """Create a modern KPI card with trend indicator."""
    # Determine trend styling
    trend_icon = "→"
    trend_color = "#fab32a"  # Default color for no trend

    if trend is not None:
        if trend > 0:
            trend_icon = "↑"
            trend_color = "#00cc96"
        elif trend < 0:
            trend_icon = "↓"
            trend_color = "#ef553b"
            trend = abs(trend)  # Make negative trend positive for display
        else:
            trend_icon = "→"
            trend_color = "#fab32a"

    # Add tooltip attribute if provided
    tooltip_attr = f'title="{tooltip}"' if tooltip else ""

    # Create the card HTML
    card_html = f"""
        <div class="metric-card" {tooltip_attr}>
            <div class="metric-title">{title}</div>
            <div class="metric-value">{prefix}{value}{unit}</div>
                <div style="display: flex; align-items: center; margin-top: 5px; font-size: 0.9rem;">
                <span style="color: {trend_color}; margin-right: 5px;">{trend_icon}</span>
                <span style="color: {trend_color};">{trend:.1f}%</span>
            </div>
        </div>
    """
    return card_html


def display_enhanced_kpi_metrics(df, filtered_df):
    """Display enhanced KPI metrics with trends."""
    st.markdown(
        """
        <div style="margin: 25px 0 15px;">
            <h2 style="font-size: 1.5rem; font-weight: 600;">Key Performance Indicators</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Calculate current period metrics
    total_hours = filtered_df["duration_seconds"].sum() / 3600
    total_earnings = filtered_df["payout_amount"].sum()

    if total_hours > 0:
        avg_hourly_rate = total_earnings / total_hours
    else:
        avg_hourly_rate = 0

    total_tasks = filtered_df["itemID"].nunique()
    active_days = filtered_df["workDate"].nunique()

    if active_days > 0:
        avg_daily_hours = total_hours / active_days
    else:
        avg_daily_hours = 0

    # Calculate trends compared to previous period of same length
    start_date = st.session_state["start_date"]
    end_date = st.session_state["end_date"]
    period_length = (end_date - start_date).days + 1

    # Get previous period with same length as current period
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=period_length - 1)

    # Make sure previous period dates are valid
    min_date = df["workDate_dt"].dt.date.min()
    if prev_start_date < min_date:
        # Adjust the previous period if it goes before available data
        prev_start_date = min_date
        prev_end_date = min_date + timedelta(days=period_length - 1)

    # Filter for previous period from the original dataframe
    prev_df = df[
        (df["workDate_dt"].dt.date >= prev_start_date)
        & (df["workDate_dt"].dt.date <= prev_end_date)
    ]

    # Calculate previous period metrics
    prev_total_hours = prev_df["duration_seconds"].sum() / 3600
    prev_total_earnings = prev_df["payout_amount"].sum()

    if prev_total_hours > 0:
        prev_avg_hourly_rate = prev_total_earnings / prev_total_hours
    else:
        prev_avg_hourly_rate = 0

    prev_total_tasks = prev_df["itemID"].nunique()
    prev_active_days = prev_df["workDate"].nunique()

    if prev_active_days > 0:
        prev_avg_daily_hours = prev_total_hours / prev_active_days
    else:
        prev_avg_daily_hours = 0

    # Calculate trend percentages
    hours_trend = calculate_trend(total_hours, prev_total_hours)
    earnings_trend = calculate_trend(total_earnings, prev_total_earnings)
    rate_trend = calculate_trend(avg_hourly_rate, prev_avg_hourly_rate)
    tasks_trend = calculate_trend(total_tasks, prev_total_tasks)
    daily_hours_trend = calculate_trend(avg_daily_hours, prev_avg_daily_hours)

    # Create enhanced KPI cards
    kpi_cols = st.columns(5)

    with kpi_cols[0]:
        st.markdown(
            create_kpi_card(
                "Total Hours",
                f"{total_hours:.1f}",
                unit=" hrs",
                trend=hours_trend,
                tooltip=f"Previous period ({prev_start_date.strftime('%b %d')} to {prev_end_date.strftime('%b %d')}): {prev_total_hours:.1f} hrs",
            ),
            unsafe_allow_html=True,
        )

    with kpi_cols[1]:
        st.markdown(
            create_kpi_card(
                "Total Earnings",
                f"{total_earnings:.2f}",
                prefix="$",
                trend=earnings_trend,
                tooltip=f"Previous period: ${prev_total_earnings:.2f}",
            ),
            unsafe_allow_html=True,
        )

    with kpi_cols[2]:
        st.markdown(
            create_kpi_card(
                "Avg. Hourly Rate",
                f"{avg_hourly_rate:.2f}",
                prefix="$",
                trend=rate_trend,
                tooltip=f"Previous period: ${prev_avg_hourly_rate:.2f}/hr",
            ),
            unsafe_allow_html=True,
        )

    with kpi_cols[3]:
        st.markdown(
            create_kpi_card(
                "Total Tasks",
                f"{total_tasks}",
                trend=tasks_trend,
                tooltip=f"Previous period: {prev_total_tasks} tasks",
            ),
            unsafe_allow_html=True,
        )

    with kpi_cols[4]:
        st.markdown(
            create_kpi_card(
                "Avg. Daily Hours",
                f"{avg_daily_hours:.1f}",
                unit=" hrs/day",
                trend=daily_hours_trend,
                tooltip=f"Previous period: {prev_avg_daily_hours:.1f} hrs/day",
            ),
            unsafe_allow_html=True,
        )


def create_daily_data(filtered_df):
    """Create enhanced daily aggregated data with additional metrics."""
    start_date = st.session_state["start_date"]
    end_date = st.session_state["end_date"]

    # Create daily aggregated data
    daily_data = (
        filtered_df.groupby("date")
        .agg({"duration_seconds": "sum", "payout_amount": "sum", "itemID": "nunique"})
        .reset_index()
    )

    # Rename columns
    daily_data = daily_data.rename(columns={"itemID": "task_count"})

    # Ensure all dates are included (even non-working days)
    date_range = pd.date_range(start=start_date, end=end_date)
    date_df = pd.DataFrame({"date": date_range})
    date_df["date"] = date_df["date"].dt.date

    daily_data = pd.merge(date_df, daily_data, on="date", how="left", validate="1:1")
    daily_data.fillna(0, inplace=True)

    # Convert seconds to hours
    daily_data["hours"] = daily_data["duration_seconds"] / 3600

    # Add day of week (0 = Monday, 6 = Sunday)
    daily_data["day_of_week"] = pd.to_datetime(daily_data["date"]).dt.dayofweek
    daily_data["day_name"] = pd.to_datetime(daily_data["date"]).dt.day_name()

    # Calculate hourly rate
    daily_data["hourly_rate"] = np.where(
        daily_data["hours"] > 0, daily_data["payout_amount"] / daily_data["hours"], 0
    )

    # Calculate rolling metrics (7-day)
    if len(daily_data) >= 7:
        daily_data["hours_7d_avg"] = (
            daily_data["hours"].rolling(window=7, min_periods=1).mean()
        )
        daily_data["earnings_7d_avg"] = (
            daily_data["payout_amount"].rolling(window=7, min_periods=1).mean()
        )
        daily_data["rate_7d_avg"] = (
            daily_data["hourly_rate"].rolling(window=7, min_periods=1).mean()
        )
    else:
        daily_data["hours_7d_avg"] = daily_data["hours"]
        daily_data["earnings_7d_avg"] = daily_data["payout_amount"]
        daily_data["rate_7d_avg"] = daily_data["hourly_rate"]

    return daily_data


def display_performance_trends(filtered_df):
    """Display enhanced performance trend analytics."""
    st.markdown(
        """
        <div style="margin: 35px 0 15px;">
            <h2 style="font-size: 1.5rem; font-weight: 600;">Overall Performance Trends</h2>
            <p style="opacity: 0.8; font-size: 0.9rem;">Analyze your performance trends over the selected period.</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Prepare daily data
    daily_data = create_daily_data(filtered_df)

    # Create a figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add hours bars
    fig.add_trace(
        go.Bar(
            x=daily_data["date"],
            y=daily_data["hours"],
            name="Hours",
            marker_color="rgba(94, 157, 245, 0.7)",
            hovertemplate="Hours: %{y:.1f}<extra></extra>",
        ),
        secondary_y=False,
    )

    # Add earnings line
    fig.add_trace(
        go.Scatter(
            x=daily_data["date"],
            y=daily_data["payout_amount"],
            name="Earnings",
            mode="lines+markers",
            marker=dict(size=8, symbol="circle", color="rgba(76, 175, 80, 0.9)"),
            line=dict(width=3, color="rgba(76, 175, 80, 0.7)"),
            hovertemplate="Earnings: $%{y:.2f}<extra></extra>",
        ),
        secondary_y=True,
    )

    # Add hourly rate as a line
    if len(daily_data) > 0 and daily_data["hourly_rate"].max() > 0:
        fig.add_trace(
            go.Scatter(
                x=daily_data["date"],
                y=daily_data["hourly_rate"],
                name="Hourly Rate",
                mode="lines",
                line=dict(width=2, color="rgba(255, 152, 0, 0.7)", dash="dot"),
                hovertemplate="Hourly Rate: $%{y:.2f}/hr<extra></extra>",
            ),
            secondary_y=True,
        )

    # Customize the layout
    fig.update_layout(
        title="",
        title_font=dict(size=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        plot_bgcolor="rgba(30, 34, 44, 0.3)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="rgba(255, 255, 255, 0.8)"),
        margin=dict(l=10, r=10, t=50, b=10),
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Hours", secondary_y=False)
    fig.update_yaxes(title_text="Amount ($)", secondary_y=True)
    fig.update_xaxes(title_text="Date")

    # Display the figure
    st.plotly_chart(fig, use_container_width=True)


def display_enhanced_payment_breakdowns(filtered_df):
    """Display enhanced payment analysis charts."""
    st.markdown(
        """
        <div style="margin: 35px 0 15px;">
            <h2 style="font-size: 1.5rem; font-weight: 600;">Payment Status Summary</h2>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Get status data
    status_data = (
        filtered_df.groupby("status")
        .agg({"payout_amount": "sum", "duration_seconds": "sum", "itemID": "nunique"})
        .reset_index()
    )

    # Calculate percentage and hours
    total_status_payout = status_data["payout_amount"].sum()
    status_data["percentage"] = (
        status_data["payout_amount"] / total_status_payout * 100
    ).round(1)
    status_data["hours"] = status_data["duration_seconds"] / 3600

    # Create gauge chart for payment status
    pending_amount = (
        status_data[status_data["status"] == "pending"]["payout_amount"].sum()
        if "pending" in status_data["status"].values
        else 0
    )
    processed_amount = (
        status_data[status_data["status"] == "processed"]["payout_amount"].sum()
        if "processed" in status_data["status"].values
        else 0
    )
    pending_percentage = (
        (pending_amount / (pending_amount + processed_amount) * 100)
        if (pending_amount + processed_amount) > 0
        else 0
    )

    # Create modern payment status cards
    st.markdown(
        f"""
    <div style="display: flex; justify-content: space-between; margin-top: 10px;">
        <div style="text-align: center; padding: 20px; background-color: rgba(255, 165, 0, 0.2); 
                    border-radius: 10px; border: 1px solid rgba(255, 165, 0, 0.3); width: 48%;">
            <h4 style="margin: 0; color: #FFA500; font-weight: 500;">Pending</h4>
            <div style="font-size: 24px; margin: 10px 0; font-weight: 600;">${pending_amount:.2f}</div>
            <div style="opacity: 0.7; font-size: 0.9rem;">{pending_percentage:.1f}% of total earnings</div>
        </div>
        <div style="text-align: center; padding: 20px; background-color: rgba(0, 128, 0, 0.2); 
                    border-radius: 10px; border: 1px solid rgba(0, 128, 0, 0.3); width: 48%;">
            <h4 style="margin: 0; color: #00cc96; font-weight: 500;">Processed</h4>
            <div style="font-size: 24px; margin: 10px 0; font-weight: 600;">${processed_amount:.2f}</div>
            <div style="opacity: 0.7; font-size: 0.9rem;">{100-pending_percentage:.1f}% of total earnings</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
