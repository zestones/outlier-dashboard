import streamlit as st
import pandas as pd
import plotly.express as px

from src.data.parse import get_date_range


def display_overview_tab(df):
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