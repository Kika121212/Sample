import streamlit as st
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor

# Function to read and normalize JSON files
def read_and_normalize(file):
    try:
        data = json.load(file)
        # Normalize the JSON data
        df = pd.json_normalize(data)
        return df
    except ValueError as e:
        st.error(f"Error reading file: {e}")
        return None

# Streamlit app
def main():
    st.title("Batsman Stats Calculator")

    uploaded_files = st.file_uploader("Upload JSON files", accept_multiple_files=True, type="json")
    
    if st.button("Calculate Stats"):
        if uploaded_files:
            # Use ThreadPoolExecutor to read and normalize files in parallel
            with ThreadPoolExecutor() as executor:
                df_list = list(executor.map(read_and_normalize, uploaded_files))

            # Filter out None values from the list
            df_list = [df for df in df_list if df is not None]
            
            # Check for 'batter' column existence
            valid_df_list = []
            for df in df_list:
                if 'batter' in df.columns:
                    valid_df_list.append(df)
                else:
                    st.error("File missing 'batter' column.")  # Log missing columns

            # Concatenate DataFrames if structures are consistent
            if valid_df_list:
                combined_df = pd.concat(valid_df_list, ignore_index=True)

                # Assuming the combined DataFrame has columns 'batter', 'runs', 'balls'
                # Group by batter and calculate the required statistics
                batter_stats = combined_df.groupby('batter').agg(
                    innings=('batter', 'count'),
                    runs=('runs', 'sum'),
                    balls=('balls', 'sum')
                ).reset_index()

                # Calculate average and strike rate
                batter_stats['average'] = batter_stats['runs'] / batter_stats['innings']
                batter_stats['strike_rate'] = (batter_stats['runs'] / batter_stats['balls']) * 100

                # Display the summary DataFrame
                st.write(batter_stats)
            else:
                st.error("No valid data found in the uploaded files.")
        else:
            st.error("Please upload at least one JSON file.")

if __name__ == "__main__":
    main()
