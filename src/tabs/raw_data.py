import streamlit as st


def raw_data_tab(df):
    st.header("Raw Data")

    # Add search functionality
    search_term = st.text_input("Search in data:", "")

    # Filter data based on search term
    if search_term:
        filtered_display_df = df[
            df.astype(str)
            .apply(lambda x: x.str.contains(search_term, case=False))
            .any(axis=1)
        ]
    else:
        filtered_display_df = df

    # Display data
    st.dataframe(filtered_display_df, use_container_width=True)

    # Add download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="work_data.csv",
        mime="text/csv",
    )
