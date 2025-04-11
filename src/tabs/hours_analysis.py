import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.data.parse import get_date_range


def display_hours_analysis_tab(df):
    start_date, end_date = get_date_range(df)
    
    st.header("Working Hours Analysis")

    # Daily hours distribution
    st.subheader("Daily Hours Distribution")

    # Aggregate hours by day
    daily_hours = (
        df.groupby("date")
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
        df.groupby(["date", "is_overtime"])
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

