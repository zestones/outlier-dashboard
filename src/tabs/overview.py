import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data.parse import get_date_range


def display_overview_tab(df):
    """Main function to display the overview tab."""
    st.header("Work Analytics Overview")

    filtered_df = display_date_range_selector(df)
    display_key_metrics(filtered_df)

    st.markdown("<hr>", unsafe_allow_html=True)
    display_work_trends(filtered_df)
    display_payment_breakdowns(filtered_df)


def display_date_range_selector(df):
    """Display date range selector and return filtered dataframe."""
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

    return filtered_df


def display_metric_card(column, title, value, prefix=""):
    """Helper function to display a metric card."""
    with column:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-title">{title}</div>'
            f'<div class="metric-value">{prefix}{value}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )


def display_key_metrics(filtered_df):
    """Calculate and display key metrics."""
    # Calculate metrics
    total_hours = filtered_df["duration_seconds"].sum() / 3600
    total_earnings = filtered_df["payout_amount"].sum()
    avg_hourly_rate = total_earnings / total_hours if total_hours > 0 else 0
    total_tasks = filtered_df["itemID"].nunique()
    active_days = filtered_df["workDate"].nunique()

    # Display metrics in columns
    cols = st.columns(5)
    display_metric_card(cols[0], "Total Hours", f"{total_hours:.2f}")
    display_metric_card(cols[1], "Total Earnings", f"{total_earnings:.2f}", "$")
    display_metric_card(cols[2], "Avg. Hourly Rate", f"{avg_hourly_rate:.2f}", "$")
    display_metric_card(cols[3], "Total Tasks", total_tasks)
    display_metric_card(cols[4], "Active Days", active_days)


def create_daily_data(filtered_df, start_date, end_date):
    """Create daily aggregated data with missing dates filled."""
    # Get start and end dates from filtered dataframe if not provided
    if start_date is None or end_date is None:
        start_date = filtered_df["workDate_dt"].dt.date.min()
        end_date = filtered_df["workDate_dt"].dt.date.max()

    # Create daily aggregated data
    daily_data = (
        filtered_df.groupby("date")
        .agg({"duration_seconds": "sum", "payout_amount": "sum"})
        .reset_index()
    )

    # Ensure all dates are included (even non-working days)
    date_range = pd.date_range(start=start_date, end=end_date)
    date_df = pd.DataFrame({"date": date_range})
    date_df["date"] = date_df["date"].dt.date

    daily_data = pd.merge(date_df, daily_data, on="date", how="left", validate="1:1")
    daily_data.fillna(0, inplace=True)

    # Convert seconds to hours
    daily_data["hours"] = daily_data["duration_seconds"] / 3600

    return daily_data


def create_trend_chart(data, x_col, y_col, title, y_label, color, add_moving_avg=True):
    """Create a trend chart with optional moving average."""
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        title=title,
        labels={x_col: "Date", y_col: y_label},
        color_discrete_sequence=[color],
    )

    # Add moving average if requested and enough data points
    if add_moving_avg and len(data) > 3:
        ma_col = f"{y_col}_ma"
        data[ma_col] = data[y_col].rolling(window=3).mean()
        fig.add_scatter(
            x=data[x_col],
            y=data[ma_col],
            mode="lines",
            name="3-Day Moving Average",
            line=dict(width=3, color="red"),
        )

    return fig


def display_work_trends(filtered_df):
    """Display work trend charts."""
    st.subheader("Work Trends")

    # Get date range
    start_date = filtered_df["workDate_dt"].dt.date.min()
    end_date = filtered_df["workDate_dt"].dt.date.max()

    # Create daily data
    daily_data = create_daily_data(filtered_df, start_date, end_date)

    # Create and display trend charts
    col1, col2 = st.columns(2)

    with col1:
        hours_fig = create_trend_chart(
            daily_data, "date", "hours", "Daily Working Hours", "Hours", "#4e8df5"
        )
        st.plotly_chart(hours_fig, use_container_width=True)

    with col2:
        earnings_fig = create_trend_chart(
            daily_data,
            "date",
            "payout_amount",
            "Daily Earnings",
            "Earnings ($)",
            "#4CAF50",
        )
        st.plotly_chart(earnings_fig, use_container_width=True)


def create_pie_chart(
    data, values_col, names_col, title, color_map=None, color_sequence=None
):
    """Create a pie chart."""
    if color_map:
        fig = px.pie(
            data,
            values=values_col,
            names=names_col,
            title=title,
            color_discrete_map=color_map,
        )
    else:
        fig = px.pie(
            data,
            values=values_col,
            names=names_col,
            title=title,
            color_discrete_sequence=color_sequence or px.colors.qualitative.Pastel,
        )

    fig.update_traces(textposition="inside", textinfo="percent+label+value")
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode="hide")

    return fig


def display_payment_status_summary(status_data):
    """Display payment status summary cards."""
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

    # Create styled status cards
    st.markdown("#### Payment Status Summary")

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; margin-top: 20px;">
            <div style="text-align: center; padding: 20px; background-color: rgba(255, 165, 0, 0.2); border-radius: 10px; width: 45%;">
                <h3 style="margin: 0; color: #FFA500;">Pending</h3>
                <p style="font-size: 24px; margin-top: 10px; font-weight: bold;">${pending_amount:.2f}</p>
            </div>
            <div style="text-align: center; padding: 20px; background-color: rgba(0, 128, 0, 0.2); border-radius: 10px; width: 45%;">
                <h3 style="margin: 0; color: #008000;">Processed</h3>
                <p style="font-size: 24px; margin-top: 10px; font-weight: bold;">${processed_amount:.2f}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def display_payment_breakdowns(filtered_df):
    """Display payment type and status breakdowns."""
    # Payment type breakdown
    st.subheader("Payment Type Breakdown")
    pay_type_data = (
        filtered_df.groupby("payType").agg({"payout_amount": "sum"}).reset_index()
    )
    pay_type_fig = create_pie_chart(
        pay_type_data, "payout_amount", "payType", "Earnings by Payment Type"
    )
    st.plotly_chart(pay_type_fig, use_container_width=True)

    # Payment status breakdown
    st.subheader("Payment Status")
    status_data = (
        filtered_df.groupby("status").agg({"payout_amount": "sum"}).reset_index()
    )

    col1, col2 = st.columns([2, 3])

    with col1:
        status_fig = create_pie_chart(
            status_data,
            "payout_amount",
            "status",
            "Earnings by Status",
            color_map={
                "pending": "#FFA500",
                "processed": "#008000",
            },
        )
        status_fig.update_traces(textinfo="percent+label")  # Simplified text info
        st.plotly_chart(status_fig, use_container_width=True)

    with col2:
        display_payment_status_summary(status_data)
