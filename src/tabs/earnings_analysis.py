import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def earnings_analysis_tab(df):
    st.header("Earnings Analysis")

    # Daily earnings
    st.subheader("Daily Earnings Breakdown")

    # Aggregate earnings by day and payment type
    daily_earnings = (
        df.groupby(["date", "payType"]).agg({"payout_amount": "sum"}).reset_index()
    )

    # Pivot the data to have payment types as columns
    earnings_pivot = daily_earnings.pivot_table(
        index="date",
        columns="payType",
        values="payout_amount",
        fill_value=0,
    ).reset_index()

    # Ensure all payTypes are included as columns
    pay_types = df["payType"].unique()
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
        df.groupby("payType")
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
    hourly_rates = df[df["hourly_rate"] > 0]["hourly_rate"].unique()

    # Aggregate earnings by hourly rate
    rate_earnings = (
        df[df["hourly_rate"] > 0]
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
        df.groupby(df["workDate_dt"].dt.strftime("%b %Y"))
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

    daily_earnings = df.groupby("date").agg({"payout_amount": "sum"}).reset_index()

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
