import streamlit as st
import pandas as pd
import plotly.express as px

def projects_details_tab(df):
    st.header("Project and Task Analysis")

    # Project breakdown
    st.subheader("Project Distribution")

    project_summary = (
        df.groupby("projectName")
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
    project_table["effective_rate"] = project_table["effective_rate"].round(2)

    project_table.columns = [
        "Project Name",
        "Total Earnings ($)",
        "Duration (s)",
        "Number of Tasks",
        "Hours Worked",
        "Effective Rate ($/hr)",
    ]

    st.dataframe(project_table.drop("Duration (s)", axis=1), use_container_width=True)

    # Task completion timeline
    st.subheader("Task Completion Timeline")

    task_timeline = df.copy()
    task_timeline["completion_date"] = pd.to_datetime(task_timeline["workDate"])

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
