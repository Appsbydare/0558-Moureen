# Section 1: Import Libraries

import streamlit as st
import pandas as pd
import datetime
import os
import base64
import json
import gspread
from google.oauth2.service_account import Credentials
from io import StringIO

# Set page configuration
st.set_page_config(
    page_title="Salary Survey Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2.B # Custom CSS to override Streamlit styling
st.markdown("""

<style>
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Minimize padding */
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }

    /* Base colors */
    :root {
        --primary-color: #0078D7;         /* Windows blue - primary accent color */
        --primary-hover: #8BDC8B;         /* Light green - hover state */
        --button-bg: #f5f5f5;             /* Light Gray - button background */
        --button-border: #e0e0e0;         /* Light Gray - button border */
        --text-primary: #333333;          /* Dark Gray - main text */
        --disabled-bg: #f0f0f0;           /* Light Gray - disabled elements */
        --disabled-text: #888888;         /* Medium Gray - disabled text */
        --tab-active: #f0f0f0;            /* Active tab background */
        --tab-inactive: #e0e0e0;          /* Inactive tab background */
    }

    /* Global button styling - consistent size and appearance */
    button, 
    .stButton > button,
    .stDownloadButton > button,
    div.stButton > button,
    [data-testid="baseButton-secondary"] {
        background-color: var(--button-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--button-border) !important;
        border-radius: 6px !important;
        padding: 4px 12px !important;
        font-size: 0.85rem !important;
        font-weight: normal !important;
        height: auto !important;
        min-height: 30px !important;
        line-height: 1.2 !important;
        white-space: nowrap !important;
        transition: all 0.2s ease !important;
        box-shadow: 2px 2px 3px rgba(0, 0, 0, 0.1) !important;
        width: auto !important;
        margin: 2px !important;
    }

    /* Hover state for all buttons - lighter green */
    button:hover, 
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    div.stButton > button:hover,
    [data-testid="baseButton-secondary"]:hover {
        background-color: var(--primary-hover) !important;
        color: var(--text-primary) !important;
        border-color: var(--primary-hover) !important;
        cursor: pointer !important;
    }

    /* Disabled button styling */
    button:disabled,
    div.stButton > button:disabled {
        background-color: var(--disabled-bg) !important;
        color: var(--disabled-text) !important;
        cursor: not-allowed !important;
        border: 1px solid var(--disabled-text) !important;
        opacity: 0.7 !important;
    }

    /* Search and Clear button styling (more compact) */
    .stButton > button {
        padding: 3px 10px !important;
        font-size: 0.8rem !important;
        min-height: 26px !important;
    }

    /* Calculate button specific styling */
    button[aria-label="Calculate"],
    .calculate-button {
        font-weight: bold !important;
        background-color: #f8f8f8 !important;
        border-color: var(--primary-color) !important;
    }

    /* Make tabs look like Windows desktop app */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 5px 24px !important;
        font-weight: 500 !important;
        border: 1px solid #ddd;
        border-bottom: none;
        border-radius: 4px 4px 0 0;
        font-size: 0.9rem !important;
        background-color: var(--tab-inactive) !important;
        color: var(--text-primary) !important;
    }

    /* Windows-style active tab */
    .stTabs [aria-selected="true"] {
        background-color: var(--tab-active) !important;
        color: var(--text-primary) !important;
        font-weight: bold !important;
        border-bottom: 1px solid var(--tab-active) !important;
        position: relative;
        z-index: 1;
    }

    /* Remove colored underline for Windows-style tabs */
    .stTabs [aria-selected="true"]::before {
        display: none !important;
    }

    /* Remove tab indicator bar for Windows-style */
    .stTabs [role="tablist"] [data-testid="stHorizontalBlock"] {
        display: none !important;
    }

    /* Remove Streamlit's element margins */
    div.element-container {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Main title */
    .main-title {
        text-align: center;
        font-size: 24px;
        font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
        margin: 2px 0;
    }

    /* Panel styling */
    [data-testid="stVerticalBlock"] > div > div[style*="flex"] > div > div[data-testid="stVerticalBlock"] {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 8px !important;
        background-color: #fcfcfc;
        margin-bottom: 10px;
    }

    /* Panel headers - Windows style */
    [data-testid="stVerticalBlock"] h3 {
        font-size: 1rem !important;
        margin-top: 0 !important;
        margin-bottom: 5px !important;
        color: var(--text-primary) !important;
        text-align: center;
        font-weight: 600 !important;
    }
    
    /* Search Panel and other panel styling to look like Windows */
    div:has(> div:contains("Search Panel")),
    div:has(> div:contains("Calculations Panel")) {
        background-color: #f5f5f5 !important;
        border: 1px solid #ddd !important;
        border-radius: 3px !important;
        margin-bottom: 10px !important;
    }
    
    /* Panel title styling */
    div:contains("Search Panel"),
    div:contains("Calculations Panel") {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        background-color: var(--tab-active) !important;
        padding: 5px 10px !important;
        border-bottom: 1px solid #ddd !important;
    }

    /* Form input styling */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input {
        padding: 0.25rem 0.4rem !important;
        height: 28px !important;
        font-size: 0.85rem !important;
        border-radius: 4px !important;
    }

    /* Make input labels smaller */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label {
        font-size: 0.85rem !important;
        margin-bottom: 2px !important;
        font-weight: 500 !important;
    }

    /* Adjustable inputs */
    .stNumberInput > div {
        flex-direction: row;
        align-items: center;
    }

    /* Number input stepper buttons */
    .stNumberInput [data-baseweb="spinner"] button {
        background-color: #fafafa !important;
        color: var(--text-primary) !important;
        border: 1px solid #e6e6e6 !important;
        min-width: 24px !important;
        width: 24px !important;
        height: 14px !important;
        padding: 0 !important;
    }

    .stNumberInput [data-baseweb="spinner"] button:hover {
        background-color: var(--primary-hover) !important;
        color: var(--text-primary) !important;
    }

    .stNumberInput button svg {
        fill: var(--primary-color) !important;
        width: 10px !important;
        height: 10px !important;
    }

    .stNumberInput button:hover svg {
        fill: var(--text-primary) !important;
    }
    
    /* Ensure the Search and Clear Filters buttons are properly displayed */
    .search-row {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        align-items: center !important;
        gap: 10px !important;
        margin-top: 5px !important;
    }

    /* Change focus color for all controls to Windows blue */
    input:focus, 
    .stSelectbox [data-baseweb="select"] > div:focus,
    .stDateInput input:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 1px var(--primary-color) !important;
    }
    
    /* Move Clear Filters button to be in the same row as Search button */
    /* First hide the original button container */
    [data-testid="stHorizontalBlock"] > div:has(button:contains("Clear Filters")) {
        display: none !important;
    }
    
    /* Then create a copy that appears next to the Search button */
    [data-testid="stHorizontalBlock"] > div:has(button:contains("Search")):after {
        content: "";
        display: inline-block;
        width: 10px;
    }
    
    /* Custom CSS to position buttons side by side */
    .search-filter-row {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        gap: 10px !important;
        margin-top: 10px !important;
    }
    
    /* Target search panel to rearrange search and clear buttons */
    div[data-testid="stVerticalBlock"]:has(div:contains("Search Panel")) {
        position: relative !important;
    }
    
    /* Force the Clear Filters button to appear next to Search button */
    button:contains("Clear Filters") {
        position: absolute !important;
        right: 100px !important;
        top: 228px !important; /* Adjust this value to align with the Search button */
    }

    /* Dropdown/select styling */
    .stSelectbox > div > div {
        min-height: 28px !important;
    }

    .stSelectbox [data-baseweb="select"] {
        font-size: 0.85rem !important;
    }

    /* Date picker more compact */
    .stDateInput > div > div {
        min-height: 28px !important;
    }

    /* Improved scrollbar styling */
    [data-testid="stDataFrame"] div::-webkit-scrollbar {
        height: 10px !important;
        width: 10px !important;
    }

    [data-testid="stDataFrame"] div::-webkit-scrollbar-thumb {
        background: #aaa;
        border-radius: 5px;
    }

    [data-testid="stDataFrame"] div::-webkit-scrollbar-track {
        background: #f1f1f1;
    }

    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        font-size: 0.85rem !important;
    }

    [data-testid="stDataFrame"] [role="cell"]:focus {
        outline-color: var(--primary-color) !important;
    }

    /* Table headers */
    [data-testid="stDataFrame"] th {
        background-color: #f0f0f0 !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        text-align: center !important;
        padding: 4px 6px !important;
    }

    /* Table cells */
    [data-testid="stDataFrame"] td {
        padding: 3px 6px !important;
    }

    /* Form button styling */
    div.stForm > div > div > div > div > button {
        width: 100% !important;
        background-color: var(--button-bg) !important;
        color: var(--text-primary) !important;
    }
    
    /* Success message styling - Windows style */
    .success-message {
        color: #107C10; /* Windows success green */
        font-size: 14px;
        font-weight: bold;
        padding: 4px;
        margin: 4px 0;
        text-align: center;
    }
    
    /* Additional styles to force Clear Filters button next to Search */
    /* This creates a direct CSS solution that works with Streamlit's structure */
    div.element-container:has(button:contains("Search")) {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        gap: 10px !important;
    }
    
    /* Search button positioning */
    button:contains("Search") {
        margin-right: 5px !important;
    }

    /* Error message styling */
    .error-message {
        color: #d32f2f;
        font-size: 14px;
        font-weight: bold;
        padding: 4px;
        margin: 4px 0;
        text-align: center;
    }
    
    /* Calculation panel labels */
    .calculation-label {
        font-size: 0.85rem !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Data editor styling */
    [data-testid="stDataEditor"] {
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f8f8f8;
        margin-bottom: 10px;
        font-size: 0.85rem !important;
    }
    
    /* Change notification styles */
    [data-testid="stNotification"] {
        background-color: #f0f8f0 !important;
        border-color: var(--primary-color) !important;
        border-radius: 4px !important;
        padding: 8px !important;
    }
    
    /* Compact layout for panels */
    div.stForm [data-testid="column"] {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }
    
    /* Ensure calculation panel controls are properly aligned and sized */
    .calculation-panel [data-testid="stHorizontalBlock"] {
        gap: 2px !important;
        align-items: center !important;
    }
    
    .calculation-panel [data-testid="stHorizontalBlock"] > div {
        min-width: 0 !important;
    }

    /* Reduce column gaps in tables */
    [data-testid="stDataFrame"] table {
        border-collapse: collapse !important;
    }
    
    [data-testid="stDataFrame"] table th,
    [data-testid="stDataFrame"] table td {
        border: 1px solid #ddd !important;
    }
    
    /* Make app container width consistent */
    .app-container {
        margin: 0 auto;
        width: 100%;
        max-width: 1200px;
    }
</style>
""", unsafe_allow_html=True)


# 2 # Google Sheets connection functions
# Google Sheets connection functions
def get_google_sheet_connection():
    # Define the scope
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']

    try:
        # Load credentials from streamlit secrets
        credentials_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(
            credentials_dict, scopes=scope)

        # Create gspread client
        gc = gspread.authorize(credentials)
        return gc
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None


def load_data_from_google_sheet():
    try:
        # Connect to Google Sheets
        gc = get_google_sheet_connection()
        if gc is None:
            return pd.DataFrame()

        # Open the spreadsheet using its ID from secrets
        sheet_id = st.secrets["gsheet"]["spreadsheet_id"]
        workbook = gc.open_by_key(sheet_id)

        # Select the specific worksheet
        worksheet = workbook.worksheet('MainDatabase')

        # Get all data from the worksheet
        data = worksheet.get_all_records()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        return df
    except Exception as e:
        st.error(f"Error loading data from Google Sheets: {e}")
        return pd.DataFrame()


def save_data_to_google_sheet(df):
    try:
        # Connect to Google Sheets
        gc = get_google_sheet_connection()
        if gc is None:
            return False

        # Open the spreadsheet using its ID from secrets
        sheet_id = st.secrets["gsheet"]["spreadsheet_id"]
        workbook = gc.open_by_key(sheet_id)

        # Select the specific worksheet
        worksheet = workbook.worksheet('MainDatabase')

        # Clear the existing data
        worksheet.clear()

        # Update the headers
        headers = df.columns.tolist()
        worksheet.append_row(headers)

        # Convert DataFrame to list of lists for insertion
        values = df.values.tolist()

        # Insert data rows
        for row in values:
            # Convert any non-serializable types to strings
            row = [str(cell) if not isinstance(cell, (str, int, float, bool, type(None))) else cell for cell in row]
            worksheet.append_row(row)

        return True
    except Exception as e:
        st.error(f"Error saving data to Google Sheets: {e}")
        return False

# 3 # Function to calculate adjustments
def calculate_adjustments(df, security_clearance, skills_adjustment, geo_differential):
    result_df = df.copy()

    # Convert percentage inputs to floats
    sec_clearance = float(security_clearance) / 100 if security_clearance else 0
    skills_adj = float(skills_adjustment) / 100 if skills_adjustment else 0
    geo_diff = float(geo_differential) / 100 if geo_differential else 0

    # Ensure Min Base is numeric by cleaning the data first
    if "Min Base" in result_df.columns:
        # Clean the Min Base column (remove $ and commas) before converting to numeric
        if result_df["Min Base"].dtype == object:  # If it's a string
            result_df["Min Base"] = result_df["Min Base"].astype(str).str.replace('$', '').str.replace(',',
                                                                                                      '').str.strip()

        # Convert to numeric
        result_df["Min Base"] = pd.to_numeric(result_df["Min Base"], errors='coerce')

        # Calculate adjustments
        result_df["Security Clearance Premium (%)"] = result_df["Min Base"] * sec_clearance
        result_df["Special Skills Premium (%)"] = result_df["Min Base"] * skills_adj
        result_df["Misc. Premium or Adjustment (%)"] = result_df["Min Base"] * geo_diff

        # Calculate total adjusted salary
        result_df["Adjusted Annual Salary"] = (
                result_df["Min Base"] +
                result_df["Security Clearance Premium (%)"] +
                result_df["Special Skills Premium (%)"] +
                result_df["Misc. Premium or Adjustment (%)"]
        )

        # Calculate hourly rate (assuming 2080 work hours per year)
        result_df["Proposed Hourly Rate"] = result_df["Adjusted Annual Salary"] / 2080

        # Format currency columns (optional - removes decimal places from dollar amounts)
        currency_cols = ["Security Clearance Premium (%)", "Special Skills Premium (%)",
                        "Misc. Premium or Adjustment (%)", "Adjusted Annual Salary"]

        for col in currency_cols:
            if col in result_df.columns:
                result_df[col] = result_df[col].round(0)

        # Format hourly rate to 2 decimal places
        if "Proposed Hourly Rate" in result_df.columns:
            result_df["Proposed Hourly Rate"] = result_df["Proposed Hourly Rate"].round(2)

    return result_df


# 4 # Initialize session state variables
if 'benchmark_data' not in st.session_state:
    try:
        # Load data from Google Sheets instead of local file
        st.session_state.benchmark_data = load_data_from_google_sheet()

        # If data is empty, initialize with default columns
        if st.session_state.benchmark_data.empty:
            st.session_state.benchmark_data = pd.DataFrame(columns=[
                "Job Code", "Job Title", "Job Family", "Job Description", "Job Level", "Industry", "Company Size",
                "Geographic Region/Location",
                "Min Base", "10 PERC", "25 PERC", "50 PERC", "75 PERC", "Max PERC",
                "TGT Min", "TGT 10", "TGT 25", "TGT 50", "TGT 75", "TGT Max",
                "Experience", "Education", "Effective Date", "Security Clearance Premium (%)",
                "Special Skills Premium (%)", "Misc. Premium or Adjustment (%)",
                "Adjusted Annual Salary", "Proposed Hourly Rate"
            ])
    except Exception as e:
        st.session_state.benchmark_data = pd.DataFrame()
        st.error(f"Error loading benchmark data: {e}")

# Initialize calculation status in session state
if 'calc_success' not in st.session_state:
    st.session_state.calc_success = False
if 'calc_error' not in st.session_state:
    st.session_state.calc_error = ""

# Initialize session state for job descriptions editing
if 'edited_rows' not in st.session_state:
    st.session_state.edited_rows = {}
if 'save_needed' not in st.session_state:
    st.session_state.save_needed = False

# Initialize session state for clear filters functionality
if 'clear_filters_clicked' not in st.session_state:
    st.session_state.clear_filters_clicked = False

# Create app title
st.markdown('<div class="main-title">Salary Survey Tool</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2 = st.tabs(["Benchmark Data", "Job Descriptions"])

# Add this function near the beginning of your script, after initializing session state variables
def reset_filters():
    """Callback function to reset the filter values"""
    if 'job_title_filter' in st.session_state:
        st.session_state.job_title_filter = ""
    if 'industry_filter' in st.session_state:
        st.session_state.industry_filter = ""
    if 'geo_region_filter' in st.session_state:
        st.session_state.geo_region_filter = ""
    # Clear calculation status
    st.session_state.calc_success = False
    st.session_state.calc_error = ""


# 5 # Benchmark Data Tab
with tab1:
    col1, col2 = st.columns(2)

    # Get unique values for dropdowns
    if not st.session_state.benchmark_data.empty:
        industries = [""] + sorted(st.session_state.benchmark_data["Industry"].unique().tolist())
        geo_regions = [""] + sorted(st.session_state.benchmark_data["Geographic Region/Location"].unique().tolist())
    else:
        industries = [""]
        geo_regions = [""]

    # Check if we need to clear filters from previous run
    if 'clear_filters_clicked' in st.session_state and st.session_state.clear_filters_clicked:
        # Reset filter values before creating the widgets
        st.session_state.job_title_filter = ""
        st.session_state.industry_filter = ""
        st.session_state.geo_region_filter = ""
        # Reset the flag
        st.session_state.clear_filters_clicked = False

    # Search Panel form with compact layout
    with col1:
        with st.form(key="search_form"):
            st.markdown(
                '<p style="text-align:center; font-weight:bold; background-color:#f5f5f5; padding:5px; border:1px solid #ddd; border-radius:5px;">Search Panel</p>',
                unsafe_allow_html=True)

            # Create a single row with 5 columns (3 inputs + 2 buttons)
            title_col, industry_col, geo_col, search_col, clear_col = st.columns([3, 3, 3, 1.5, 1.5])

            # Job Title in first column
            with title_col:
                st.markdown('<div style="padding-top:2px;">Job Title:</div>', unsafe_allow_html=True)
                job_title_filter = st.text_input("", label_visibility="collapsed", key="job_title_filter")

            # Industry in second column
            with industry_col:
                st.markdown('<div style="padding-top:2px;">Industry:</div>', unsafe_allow_html=True)
                industry_filter = st.selectbox(
                    "",
                    industries,
                    label_visibility="collapsed",
                    key="industry_filter"
                )

            # Geo Region/Location in third column
            with geo_col:
                st.markdown('<div style="padding-top:2px;">Geo Region/Location:</div>', unsafe_allow_html=True)
                geo_region_filter = st.selectbox(
                    "",
                    geo_regions,
                    label_visibility="collapsed",
                    key="geo_region_filter"
                )

            # Search button in fourth column
            with search_col:
                st.markdown('<div style="padding-top:2px;">&nbsp;</div>', unsafe_allow_html=True)
                search_button = st.form_submit_button("Search")

            # Clear button in fifth column - MODIFIED TO USE CALLBACK
            with clear_col:
                st.markdown('<div style="padding-top:2px;">&nbsp;</div>', unsafe_allow_html=True)
                clear_filters = st.form_submit_button("Clear", on_click=reset_filters)

    # Calculations Panel form with compact layout
    with col2:
        with st.form(key="calc_form"):
            st.markdown(
                '<p style="text-align:center; font-weight:bold; background-color:#f5f5f5; padding:5px; border:1px solid #ddd; border-radius:5px;">Calculations Panel</p>',
                unsafe_allow_html=True)

            # Create a single row with 5 columns (4 inputs + 1 button)
            sec_col, skills_col, geo_diff_col, date_col, calc_col = st.columns([3, 3, 3, 3, 2])

            # Security Clearance in first column - smaller font label
            with sec_col:
                st.markdown('<div style="padding-top:2px; font-size:0.9rem;">Security Clearance (%):</div>',
                           unsafe_allow_html=True)
                security_clearance = st.number_input("", min_value=0.0, max_value=100.0, step=0.1, format="%.1f",
                                                    label_visibility="collapsed", key="security_clearance")

            # Skills Adjustment in second column - smaller font label
            with skills_col:
                st.markdown('<div style="padding-top:2px; font-size:0.9rem;">Skills Adjustment (%):</div>',
                           unsafe_allow_html=True)
                skills_adjustment = st.number_input("", min_value=0.0, max_value=100.0, step=0.1, format="%.1f",
                                                   label_visibility="collapsed", key="skills_adjustment")

            # Geo Differential in third column - smaller font label
            with geo_diff_col:
                st.markdown('<div style="padding-top:2px; font-size:0.9rem;">Geo Differential (%):</div>',
                           unsafe_allow_html=True)
                geo_differential = st.number_input("", min_value=0.0, max_value=100.0, step=0.1, format="%.1f",
                                                  label_visibility="collapsed", key="geo_differential")

            # Effective Date in fourth column - smaller font label
            with date_col:
                st.markdown('<div style="padding-top:2px; font-size:0.9rem;">Effective Date:</div>',
                           unsafe_allow_html=True)
                effective_date = st.date_input("", datetime.datetime.now(), label_visibility="collapsed",
                                              key="effective_date")

            # Calculate button in fifth column
            with calc_col:
                st.markdown('<div style="padding-top:2px;">&nbsp;</div>', unsafe_allow_html=True)
                calculate_clicked = st.form_submit_button("Calculate")

    # REMOVED: original handling of clear_filters button that was causing the error
    # The reset_filters callback handles this functionality now

    # Initialize session state variables for export
    if 'display_download_link' not in st.session_state:
        st.session_state.display_download_link = False
    if 'export_csv' not in st.session_state:
        st.session_state.export_csv = None
    if 'export_filename' not in st.session_state:
        st.session_state.export_filename = None

    # Filter and display data
    if not st.session_state.benchmark_data.empty:
        filtered_data = st.session_state.benchmark_data.copy()

        # Apply filters if they exist
        if job_title_filter:
            filtered_data = filtered_data[
                filtered_data["Job Title"].str.contains(job_title_filter, case=False, na=False)
            ]
        if industry_filter:
            filtered_data = filtered_data[filtered_data["Industry"] == industry_filter]
        if geo_region_filter:
            filtered_data = filtered_data[filtered_data["Geographic Region/Location"] == geo_region_filter]

        # Apply calculations if the button was clicked
        if calculate_clicked:
            try:
                # Call the calculation function with the form values
                filtered_data = calculate_adjustments(
                    filtered_data,
                    security_clearance,
                    skills_adjustment,
                    geo_differential
                )
                # Set success message in session state
                st.session_state.calc_success = True
                st.session_state.calc_error = ""

                # Store the calculated data in session state
                st.session_state.calculated_data = filtered_data.copy()
            except Exception as e:
                # Set error message in session state
                st.session_state.calc_success = False
                st.session_state.calc_error = str(e)
                st.error(f"Error: {st.session_state.calc_error}")

        # If we have calculated data in session state, use that instead
        if 'calculated_data' in st.session_state and st.session_state.calc_success:
            # Check if our current filters match the calculated data
            current_filter_match = True
            calc_data = st.session_state.calculated_data

            # Only use session state data if the filters match
            if job_title_filter and not all(
                    calc_data["Job Title"].str.contains(job_title_filter, case=False, na=False)):
                current_filter_match = False
            if industry_filter and not all(calc_data["Industry"] == industry_filter):
                current_filter_match = False
            if geo_region_filter and not all(calc_data["Geographic Region/Location"] == geo_region_filter):
                current_filter_match = False

            if current_filter_match:
                filtered_data = calc_data

        # Display the filtered and possibly calculated data, excluding Job Family and Job Description columns
        display_columns = [col for col in filtered_data.columns if col not in ["Job Family", "Job Description"]]
        st.dataframe(filtered_data[display_columns], use_container_width=True, height=400)

        # Action buttons at the bottom
        col1, col2, col3 = st.columns([2, 1, 1])

        with col2:
            # Export button
            if not filtered_data.empty:
                # When Export button is clicked, prepare the CSV but don't display it yet
                if st.button("Export Data"):
                    # Create export CSV data
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    export_filename = f"salary_data_export_{timestamp}.csv"

                    # Store in session state
                    st.session_state.export_csv = filtered_data.to_csv(index=False).encode()
                    st.session_state.export_filename = export_filename
                    st.session_state.display_download_link = True

                    # Force rerun to display the download link
                    try:
                        st.rerun()  # Updated from st.experimental_rerun()
                    except:
                        st.success("Please refresh the page to download your data.")

        # Display download link if export was requested
        if st.session_state.display_download_link:
            b64 = base64.b64encode(st.session_state.export_csv).decode()
            download_href = f'<a href="data:file/csv;base64,{b64}" download="{st.session_state.export_filename}">Download CSV File</a>'
            st.markdown(download_href, unsafe_allow_html=True)
            st.success("Your data is ready for download")

            # Add a button to clear the download link
            if st.button("Clear Download"):
                st.session_state.display_download_link = False
                try:
                    st.rerun()  # Updated from st.experimental_rerun()
                except:
                    st.warning("Please refresh the page to clear the download link.")



    else:
        st.info("No benchmark data available. Please upload a file.")
# Define a callback function to reset job search filters
def reset_job_filters():
    """Callback function to reset job search filters"""
    if 'job_code_search' in st.session_state:
        st.session_state.job_code_search = ""
    if 'job_title_search' in st.session_state:
        st.session_state.job_title_search = ""
    if 'job_family_search' in st.session_state:
        st.session_state.job_family_search = ""


# 6 # Job Descriptions Tab
# Job Descriptions Tab

# Job Descriptions Tab
with tab2:
    # Initialize session state for job descriptions if not already done
    if 'edited_jobs' not in st.session_state:
        st.session_state.edited_jobs = {}
    if 'editing_in_progress' not in st.session_state:
        st.session_state.editing_in_progress = False
    if 'save_in_progress' not in st.session_state:
        st.session_state.save_in_progress = False
    if 'save_success_message' not in st.session_state:
        st.session_state.save_success_message = ""

    # Search Panel form for Job Descriptions
    with st.form(key="job_search_form"):
        st.markdown(
            '<p style="text-align:center; font-weight:bold; background-color:#f5f5f5; padding:5px; border:1px solid #ddd; border-radius:5px;">Search Panel</p>',
            unsafe_allow_html=True)

        # Create a single row with 4 columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown('<div style="padding-top:2px;">Job Code:</div>', unsafe_allow_html=True)
            job_code_search = st.text_input("", label_visibility="collapsed", key="job_code_search")

        with col2:
            st.markdown('<div style="padding-top:2px;">Job Title:</div>', unsafe_allow_html=True)
            job_title_search = st.text_input("", label_visibility="collapsed", key="job_title_search")

        with col3:
            st.markdown('<div style="padding-top:2px;">Job Family:</div>', unsafe_allow_html=True)
            job_family_search = st.text_input("", label_visibility="collapsed", key="job_family_search")

        with col4:
            st.markdown('<div style="padding-top:2px;">&nbsp;</div>', unsafe_allow_html=True)
            search_jobs = st.form_submit_button("Search")

        # Clear button with callback
        col1, col2 = st.columns([1, 1])
        with col1:
            clear_job_filters = st.form_submit_button("Clear Filters", on_click=reset_job_filters)

    # Display status message if it exists
    if st.session_state.save_success_message:
        st.success(st.session_state.save_success_message)
        # Clear the message after displaying once
        st.session_state.save_success_message = ""

    # Filter job descriptions from benchmark data
    if not st.session_state.benchmark_data.empty:
        # Extract just the job description columns we need
        job_desc_columns = ["Job Code", "Job Title", "Job Family", "Job Description"]

        # Make sure all required columns exist
        if all(col in st.session_state.benchmark_data.columns for col in job_desc_columns):
            # Create a display dataframe with only the columns we need
            display_df = st.session_state.benchmark_data[job_desc_columns].copy()

            # Apply filters if they exist
            if job_code_search:
                display_df = display_df[
                    display_df["Job Code"].astype(str).str.contains(job_code_search, case=False, na=False)
                ]
            if job_title_search:
                display_df = display_df[
                    display_df["Job Title"].astype(str).str.contains(job_title_search, case=False, na=False)
                ]
            if job_family_search:
                display_df = display_df[
                    display_df["Job Family"].astype(str).str.contains(job_family_search, case=False, na=False)
                ]

            # Convert Job Family and Job Description to string before editing
            display_df['Job Family'] = display_df['Job Family'].astype(str)
            display_df['Job Description'] = display_df['Job Description'].astype(str)

            # Display filtered data with editable cells
            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                num_rows="fixed",
                height=400,
                column_config={
                    "Job Code": st.column_config.TextColumn("Job Code", disabled=True),
                    "Job Title": st.column_config.TextColumn("Job Title", disabled=True),
                    "Job Family": st.column_config.TextColumn("Job Family"),
                    "Job Description": st.column_config.TextColumn("Job Description", width="large")
                },
                hide_index=True,
                key="job_descriptions_data_editor"
            )

            # Check for changes between the original and edited dataframes
            has_changes = False
            edited_jobs = {}

            # Compare the original display_df with the edited_df
            if edited_df is not None:
                for index, row in edited_df.iterrows():
                    job_code = row["Job Code"]
                    original_row = display_df.loc[display_df["Job Code"] == job_code]

                    if len(original_row) > 0:
                        # Check if Job Family was changed
                        if row["Job Family"] != original_row["Job Family"].values[0]:
                            has_changes = True
                            if job_code not in edited_jobs:
                                edited_jobs[job_code] = {}
                            edited_jobs[job_code]["Job Family"] = row["Job Family"]

                        # Check if Job Description was changed
                        if row["Job Description"] != original_row["Job Description"].values[0]:
                            has_changes = True
                            if job_code not in edited_jobs:
                                edited_jobs[job_code] = {}
                            edited_jobs[job_code]["Job Description"] = row["Job Description"]

            # Store edited jobs in session state for use in save operation
            if has_changes:
                st.session_state.edited_jobs = edited_jobs
                st.session_state.editing_in_progress = True

            # Buttons at the bottom
            job_col1, job_col2, job_col3 = st.columns([3, 1, 1])

            with job_col3:
                # Save Changes button - only enabled if there are changes to save
                if st.session_state.editing_in_progress and not st.session_state.save_in_progress:
                    save_button = st.button("Save Changes", type="primary")
                    if save_button:
                        # Set save in progress flag
                        st.session_state.save_in_progress = True

                        try:
                            # Get the original benchmark data
                            original_df = st.session_state.benchmark_data.copy()
                            changes_made = False

                            # Apply each edit to the relevant rows in the original dataframe
                            for job_code, changes in st.session_state.edited_jobs.items():
                                # Find the row with this job code
                                row_indices = original_df.index[original_df["Job Code"] == job_code].tolist()

                                if row_indices:
                                    row_idx = row_indices[0]
                                    # Update only the Job Family and Job Description columns if they were changed
                                    if "Job Family" in changes:
                                        original_df.loc[row_idx, "Job Family"] = changes["Job Family"]
                                        changes_made = True

                                    if "Job Description" in changes:
                                        original_df.loc[row_idx, "Job Description"] = changes["Job Description"]
                                        changes_made = True

                            if changes_made:
                                # Save the updated dataframe back to session state
                                st.session_state.benchmark_data = original_df

                                # Save to Google Sheets
                                save_success = save_data_to_google_sheet(original_df)

                                if save_success:
                                    # Set success message to be displayed after rerun
                                    st.session_state.save_success_message = "Job descriptions updated successfully!"
                                    # Reset editing flags
                                    st.session_state.edited_jobs = {}
                                    st.session_state.editing_in_progress = False
                                else:
                                    st.error("Failed to save to Google Sheets. Please try again.")
                            else:
                                st.info("No changes were detected to save.")
                                st.session_state.edited_jobs = {}
                                st.session_state.editing_in_progress = False

                        except Exception as e:
                            st.error(f"Error during save operation: {str(e)}")

                        # Reset save in progress flag
                        st.session_state.save_in_progress = False

                else:
                    # Disabled save button when no changes or operation in progress
                    save_disabled = not st.session_state.editing_in_progress or st.session_state.save_in_progress
                    st.button("Save Changes", disabled=save_disabled)

                    # Show save in progress message
                    if st.session_state.save_in_progress:
                        st.info("Save operation in progress...")
        else:
            missing_cols = [col for col in job_desc_columns if col not in st.session_state.benchmark_data.columns]
            st.error(f"Missing required columns in benchmark data: {', '.join(missing_cols)}")
    else:
        st.info("No benchmark data available. Please upload a file.")

