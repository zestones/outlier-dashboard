import pandas as pd
import re
import streamlit as st


# Helper functions for data processing
def parse_duration(duration_str):
    """Parse duration strings like '1h 15m' or '32m 45s' into total seconds"""
    if duration_str == "-":
        return 0

    hours, minutes, seconds = 0, 0, 0

    # Look for hours
    hour_match = re.search(r"(\d+)h", duration_str)
    if hour_match:
        hours = int(hour_match.group(1))

    # Look for minutes
    minute_match = re.search(r"(\d+)m", duration_str)
    if minute_match:
        minutes = int(minute_match.group(1))

    # Look for seconds
    second_match = re.search(r"(\d+)s", duration_str)
    if second_match:
        seconds = int(second_match.group(1))

    return hours * 3600 + minutes * 60 + seconds


def extract_rate(rate_str):
    """Extract the hourly rate from strings like '$45.00/hr'"""
    if rate_str == "-":
        return 0

    rate_match = re.search(r"\$(\d+\.\d+)", rate_str)
    if rate_match:
        return float(rate_match.group(1))
    return 0


def extract_payout(payout_str):
    """Extract the payout amount from strings like '$56.25'"""
    if payout_str == "-":
        return 0

    payout_match = re.search(r"\$(\d+\.\d+)", payout_str)
    if payout_match:
        return float(payout_match.group(1))
    return 0


def format_duration(seconds):
    """Format seconds into a readable time string"""
    if seconds == 0:
        return "-"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def format_money(amount):
    """Format amount as money with $ sign"""
    return f"${amount:.2f}"


def get_date_range(df):
    """Get min and max dates from dataframe"""
    min_date = pd.to_datetime(df["workDate"]).min()
    max_date = pd.to_datetime(df["workDate"]).max()
    return min_date, max_date


def fill_missing_dates(df, date_col="workDate"):
    """Fill in missing dates with zero values"""
    # Get min and max dates
    min_date, max_date = get_date_range(df)

    # Create a complete date range
    date_range = pd.date_range(start=min_date, end=max_date, freq="D")

    # Create a template dataframe with all dates
    template_df = pd.DataFrame({date_col: date_range})
    template_df[date_col] = template_df[date_col].dt.strftime("%b %d, %Y")

    # Perform groupby aggregation on the original dataframe
    daily_df = (
        df.groupby(date_col)
        .agg({"duration_seconds": "sum", "payout_amount": "sum"})
        .reset_index()
    )

    # Merge with template to include all dates
    complete_df = pd.merge(template_df, daily_df, on=date_col, how="left")
    complete_df.fillna(0, inplace=True)

    return complete_df


# Function to process the uploaded CSV file
def process_data(df):
    # Convert workDate to datetime for easier handling
    try:
        # First, make a copy to avoid modifying the original dataframe
        df = df.copy()

        # Convert workDate to datetime, handling various possible formats
        df["workDate_dt"] = pd.to_datetime(
            df["workDate"], format="%b %d, %Y", errors="coerce"
        )
        if df["workDate_dt"].isnull().all():
            # Try alternative format if the first attempt failed
            df["workDate_dt"] = pd.to_datetime(df["workDate"], errors="coerce")

        # Parse durations into seconds
        df["duration_seconds"] = df["duration"].apply(parse_duration)

        # Extract hourly rates and payout amounts
        df["hourly_rate"] = df["rateApplied"].apply(extract_rate)
        df["payout_amount"] = df["payout"].apply(extract_payout)

        # Add week number and month name for grouping
        df["week"] = df["workDate_dt"].dt.isocalendar().week
        df["month"] = df["workDate_dt"].dt.month_name()
        df["day_of_week"] = df["workDate_dt"].dt.day_name()
        df["date"] = df["workDate_dt"].dt.date

        # Create a flag for overtime work
        df["is_overtime"] = df["payType"] == "overtimePay"

        return df

    except Exception as e:
        st.error(f"Error in process_data: {str(e)}")
        st.write("Sample of problematic data:")
        st.write(df["workDate"].head())
        raise e
