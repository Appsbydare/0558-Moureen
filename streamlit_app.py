# Section 1: Import Libraries
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import base64
import json
import gspread
from google.oauth2.service_account import Credentials
from io import StringIO
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(
    page_title="TCC Comp Data Tool",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to override Streamlit styling
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
        font-size: 28px;
        font-family: Impact, Haettenschweiler, 'Arial Narrow Bold', sans-serif;
        margin: 0px 0;
    }

    /* Panel styling */
    [data-testid="stVerticalBlock"] > div > div[style*="flex"] > div > div[data-testid="stVerticalBlock"] {
        border: 1px solid #e0e0e0;
        border-radius: 2px;
        padding: 8px !important;
        background-color: #fcfcfc;
        margin-bottom: 2px;
    }

    /* Panel headers - Windows style */
    [data-testid="stVerticalBlock"] h3 {
        font-size: 1rem !important;
        margin-top: 0 !important;
        margin-bottom: 2px !important;
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
        margin-bottom: 2px !important;
    }

    /* Panel title styling */
    div:contains("Search Panel"),
    div:contains("Calculations Panel") {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        background-color: var(--tab-active) !important;
        padding: 2px 10px !important;
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

    /* Search button positioning */
    button:contains("Search") {
        margin-right: 5px !important;
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
        min-height: 24px !important;
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
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        font-size: 0.85rem !important;
    }

    [data-testid="stDataFrame"] [role="cell"]:focus, [data-testid="stDataEditor"] [role="cell"]:focus {
        outline-color: var(--primary-color) !important;
    }

    /* Table headers */
    [data-testid="stDataFrame"] th, [data-testid="stDataEditor"] th {
        background-color: #f0f0f0 !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        text-align: center !important;
        padding: 4px 6px !important;
    }

    /* Table cells */
    [data-testid="stDataFrame"] td, [data-testid="stDataEditor"] td {
        padding: 1px 6px !important;
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

    /* Error message styling */
    .error-message {
        color: #d32f2f;
        font-size: 14px;
        font-weight: bold;
        padding: 1px;
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
    [data-testid="stDataFrame"] table, [data-testid="stDataEditor"] table {
        border-collapse: collapse !important;
    }

    [data-testid="stDataFrame"] table th,
    [data-testid="stDataFrame"] table td,
    [data-testid="stDataEditor"] table th,
    [data-testid="stDataEditor"] table td {
        border: 1px solid #ddd !important;
    }

    /* Make app container width consistent */
    .app-container {
        margin: 0 auto;
        width: 100%;
        max-width: 1200px;
    }

    /* Spinner for saving indicator */
    .spinner {
        width: 20px;
        height: 20px;
        border: 3px solid rgba(0, 0, 0, 0.1);
        border-radius: 50%;
        border-top-color: #3498db;
        animation: spin 1s ease-in-out infinite;
        display: inline-block;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Success message styling */
    .success-message {
        color: #28a745;
        font-weight: 500;
        padding: 5px 0;
    }

    /* Checkbox styling for row selection */
    .stCheckbox > div {
        min-height: 28px !important;
    }

    .stCheckbox [data-baseweb="checkbox"] {
        margin-bottom: 0 !important;
    }

    /* Admin access styling */
    .admin-panel {
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }

    .admin-panel h3 {
        font-size: 1rem !important;
        margin-top: 0 !important;
        margin-bottom: 10px !important;
    }

    /* Password input styling */
    .password-input {
        margin-bottom: 10px;
    }

    /* Help text styling */
    .help-text {
        font-size: 0.85rem;
        color: #555;
        margin-top: 5px;
    }

    /* Format the dataframe selection column */
    .selection-col {
        text-align: center;
        width: 30px;
    }
</style>
""", unsafe_allow_html=True)


# Part 2 ####################################
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


def open_google_sheet():
    """Generate a link to open the Google Sheet directly"""
    try:
        sheet_id = st.secrets["gsheet"]["spreadsheet_id"]
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
        return sheet_url
    except Exception as e:
        st.error(f"Error generating Google Sheet link: {e}")
        return None


# Function to calculate adjustments with corrected date handling
def calculate_adjustments(df, effective_date_input, security_clearance, skills_adjustment, geo_differential):
    result_df = df.copy()

    # Convert percentage inputs to floats
    sec_clearance = float(security_clearance) / 100 if security_clearance else 0
    skills_adj = float(skills_adjustment) / 100 if skills_adjustment else 0
    geo_diff = float(geo_differential) / 100 if geo_differential else 0

    # Ensure Min Base is numeric by cleaning the data first
    if "Min" in result_df.columns:
        # Clean the Min column (remove $ and commas) before converting to numeric
        if result_df["Min"].dtype == object:  # If it's a string
            result_df["Min"] = result_df["Min"].astype(str).str.replace('$', '').str.replace(',',
                                                                                                       '').str.strip()

        # Convert to numeric
        result_df["Min"] = pd.to_numeric(result_df["Min"], errors='coerce')

        # Convert Effective Date from the database to datetime for comparison
        result_df["Effective Date"] = pd.to_datetime(result_df["Effective Date"], errors='coerce')

        # Convert effective_date_input to pandas Timestamp for consistent date comparison
        # This is the key fix - ensure effective_date_input is the same type as the dates in the dataframe
        effective_date_input_dt = pd.Timestamp(effective_date_input)

        # Format the Effective Date to show only the date portion (not time)
        result_df["Effective Date"] = result_df["Effective Date"].dt.date

        # Calculate date difference and effective date adjustment (3% per year)
        def calculate_effective_date_adjustment(row):
            if pd.isnull(row["Effective Date"]):
                return 0

            # Convert both dates to the same type (datetime.date) before subtraction
            # This is the fix for the unsupported operand error
            effective_date_as_date = effective_date_input_dt.date()
            db_date = row["Effective Date"]

            # Calculate the difference in days
            date_diff_days = (effective_date_as_date - db_date).days
            date_diff_years = date_diff_days // 365.25  # Integer division with //

            # Calculate adjustment amount (3% per year of base salary)
            adjustment_amount = row["Min"] * (date_diff_years * 0.03)

            return adjustment_amount

        # Apply the calculation to each row
        result_df["Effective Date Adjustment"] = result_df.apply(calculate_effective_date_adjustment, axis=1)

        # Base salary after date adjustment
        result_df["Base After Date Adjustment"] = result_df["Min"] + result_df["Effective Date Adjustment"]

        # Calculate other adjustments based on the date-adjusted base salary
        result_df["Security Clearance Premium (%)"] = result_df["Base After Date Adjustment"] * sec_clearance
        result_df["Special Skills Premium (%)"] = result_df["Base After Date Adjustment"] * skills_adj
        result_df["Misc. Premium or Adjustment (%)"] = result_df["Base After Date Adjustment"] * geo_diff

        # Calculate total adjusted salary
        result_df["Adjusted Annual Salary"] = (
                result_df["Base After Date Adjustment"] +
                result_df["Security Clearance Premium (%)"] +
                result_df["Special Skills Premium (%)"] +
                result_df["Misc. Premium or Adjustment (%)"]
        )

        # Calculate hourly rate (assuming 2080 work hours per year)
        result_df["Proposed Hourly Rate"] = result_df["Adjusted Annual Salary"] / 2080

        # Format currency columns (optional - removes decimal places from dollar amounts)
        currency_cols = ["Effective Date Adjustment", "Security Clearance Premium (%)",
                         "Special Skills Premium (%)", "Misc. Premium or Adjustment (%)",
                         "Adjusted Annual Salary"]

        for col in currency_cols:
            if col in result_df.columns:
                result_df[col] = result_df[col].round(0)

        # Format hourly rate to 2 decimal places
        if "Proposed Hourly Rate" in result_df.columns:
            result_df["Proposed Hourly Rate"] = result_df["Proposed Hourly Rate"].round(2)

        # Drop the temporary calculation column
        if "Base After Date Adjustment" in result_df.columns:
            result_df = result_df.drop(columns=["Base After Date Adjustment"])

    return result_df


# Initialize session state variables
if 'benchmark_data' not in st.session_state:
    try:
        # Load data from Google Sheets instead of local file
        st.session_state.benchmark_data = load_data_from_google_sheet()

        # If data is empty, initialize with default columns
        if st.session_state.benchmark_data.empty:
            st.session_state.benchmark_data = pd.DataFrame(columns=[
                "Job Code", "Job Title", "Company Size",
                "Geographic Region/Location",
                "Min Base", "10 PERC", "25 PERC", "50 PERC", "75 PERC", "Max PERC",
                "TGT Min", "TGT 10", "TGT 25", "TGT 50", "TGT 75", "TGT Max",
                "Experience", "Education", "Effective Date", "Effective Date Adjustment",
                "Security Clearance Premium (%)", "Special Skills Premium (%)",
                "Misc. Premium or Adjustment (%)", "Adjusted Annual Salary",
                "Proposed Hourly Rate"
            ])
    except Exception as e:
        st.session_state.benchmark_data = pd.DataFrame()
        st.error(f"Error loading benchmark data: {e}")

# Initialize other session state variables
if 'last_successful_save' not in st.session_state:
    st.session_state.last_successful_save = False

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

# Initialize session state for row selection
if 'selected_rows' not in st.session_state:
    st.session_state.selected_rows = []
if 'select_all' not in st.session_state:
    st.session_state.select_all = False

# Initialize admin authentication
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"  # Default password, can be changed


# Add this function for resetting search filters
def reset_filters():
    """Callback function to reset the filter values"""
    if 'job_title_filter' in st.session_state:
        st.session_state.job_title_filter = ""
    if 'geo_region_filter' in st.session_state:
        st.session_state.geo_region_filter = ""
    # Clear calculation status
    st.session_state.calc_success = False
    st.session_state.calc_error = ""
    # Reset selection
    st.session_state.selected_rows = []
    st.session_state.select_all = False


# Function to toggle select all rows
def toggle_select_all():
    st.session_state.select_all = not st.session_state.select_all
    if st.session_state.select_all:
        # If select all is checked, select all visible rows
        if 'filtered_data' in st.session_state:
            st.session_state.selected_rows = st.session_state.filtered_data['Job Code'].tolist()
    else:
        # If select all is unchecked, clear selection
        st.session_state.selected_rows = []


# Function to toggle row selection
def toggle_row_selection(job_code):
    if job_code in st.session_state.selected_rows:
        st.session_state.selected_rows.remove(job_code)
    else:
        st.session_state.selected_rows.append(job_code)


# Function to verify admin password
def verify_admin_password():
    entered_password = st.session_state.password_input
    if entered_password == st.session_state.admin_password:
        st.session_state.admin_authenticated = True
    else:
        st.error("Incorrect password")


# Define a callback function to reset job search filters
def reset_job_filters():
    """Callback function to reset job search filters"""
    if 'job_code_search' in st.session_state:
        st.session_state.job_code_search = ""
    if 'job_title_search' in st.session_state:
        st.session_state.job_title_search = ""
    if 'job_family_search' in st.session_state:
        st.session_state.job_family_search = ""

# Part 3 #######################################################


# Create app title
st.markdown('<div class="main-title">TCC Comp Data Tool</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Benchmark Data", "Job Descriptions", "Administration"])

# 5 # Benchmark Data Tab
with tab1:
    col1, col2 = st.columns(2)

    # Get unique values for dropdowns
    if not st.session_state.benchmark_data.empty:
        geo_regions = [""] + sorted(st.session_state.benchmark_data["Geographic Region/Location"].unique().tolist())
    else:
        geo_regions = [""]

    # Check if we need to clear filters from previous run
    if 'clear_filters_clicked' in st.session_state and st.session_state.clear_filters_clicked:
        # Reset filter values before creating the widgets
        st.session_state.job_title_filter = ""
        st.session_state.geo_region_filter = ""
        # Reset the flag
        st.session_state.clear_filters_clicked = False

    # Search Panel form with compact layout - USING UNIQUE KEY
    with col1:
        with st.form(key="search_form_benchmark"):  # CHANGED KEY HERE
            st.markdown(
                '<p style="text-align:center; font-weight:bold; background-color:#f5f5f5; padding:5px; border:1px solid #ddd; border-radius:5px;">Search Panel</p>',
                unsafe_allow_html=True)

            # Create a single row with 4 columns (2 inputs + 2 buttons)
            title_col, geo_col, search_col, clear_col = st.columns([4, 4, 1.5, 1.5])

            # Job Title in first column
            with title_col:
                st.markdown('<div style="padding-top:1px;">Job Title:</div>', unsafe_allow_html=True)
                job_title_filter = st.text_input("", label_visibility="collapsed", key="job_title_filter")

            # Geo Region/Location in third column
            with geo_col:
                st.markdown('<div style="padding-top:1px;">Geo Region/Location:</div>', unsafe_allow_html=True)
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

            # Clear button in fifth column
            with clear_col:
                st.markdown('<div style="padding-top:2px;">&nbsp;</div>', unsafe_allow_html=True)
                clear_filters = st.form_submit_button("Clear", on_click=reset_filters)

    # Calculations Panel form with compact layout - USING UNIQUE KEY
    with col2:
        with st.form(key="calc_form_benchmark"):  # CHANGED KEY HERE
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

            # Skills Adjustment in second column - smaller font label - Default set to 0.0
            with skills_col:
                st.markdown('<div style="padding-top:2px; font-size:0.9rem;">Skills Adjustment (%):</div>',
                            unsafe_allow_html=True)
                skills_adjustment = st.number_input("", min_value=-100.0, max_value=100.0, step=0.1, format="%.1f",
                                                    label_visibility="collapsed", key="skills_adjustment", value=0.0)

            # Geo Differential in third column - smaller font label - Default set to 0.0
            with geo_diff_col:
                st.markdown('<div style="padding-top:2px; font-size:0.9rem;">Geo Differential (%):</div>',
                            unsafe_allow_html=True)
                geo_differential = st.number_input("", min_value=-100.0, max_value=100.0, step=0.1, format="%.1f",
                                                   label_visibility="collapsed", key="geo_differential", value=0.0)

            # Effective Date in fourth column - Explicitly using MM/DD/YYYY format
            with date_col:
                st.markdown('<div style="padding-top:2px; font-size:0.9rem;">Effective Date:</div>',
                            unsafe_allow_html=True)
                # Changed the label to explicitly mention MM/DD/YYYY format
                effective_date = st.date_input("", datetime.date.today(),
                                               label_visibility="collapsed", key="effective_date",
                                               format="MM/DD/YYYY")  # Setting the format explicitly to MM/DD/YYYY

            # Calculate button in fifth column
            with calc_col:
                st.markdown('<div style="padding-top:2px;">&nbsp;</div>', unsafe_allow_html=True)
                calculate_clicked = st.form_submit_button("Calculate")

    # Initialize session state variables for export
    if 'display_download_link' not in st.session_state:
        st.session_state.display_download_link = False
    if 'export_csv' not in st.session_state:
        st.session_state.export_csv = None
    if 'export_filename' not in st.session_state:
        st.session_state.export_filename = None

    # Initialize selection state if not already done
    if 'selected_rows' not in st.session_state:
        st.session_state.selected_rows = []
    if 'select_all' not in st.session_state:
        st.session_state.select_all = False


# Part 4 ######################################################

# Continue Benchmark Data Tab from Part 3
with tab1:
    # Filter and display data
    if not st.session_state.benchmark_data.empty:
        filtered_data = st.session_state.benchmark_data.copy()

        # Apply filters if they exist
        if job_title_filter:
            filtered_data = filtered_data[
                filtered_data["Job Title"].str.contains(job_title_filter, case=False, na=False)
            ]
        if geo_region_filter:
            filtered_data = filtered_data[filtered_data["Geographic Region/Location"] == geo_region_filter]

        # Store filtered data in session state for select all functionality
        st.session_state.filtered_data = filtered_data.copy()

        # Apply calculations if the button was clicked
        if calculate_clicked:
            try:
                # Call the calculation function with the form values
                filtered_data = calculate_adjustments(
                    filtered_data,
                    effective_date,
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
            if geo_region_filter and not all(calc_data["Geographic Region/Location"] == geo_region_filter):
                current_filter_match = False

            if current_filter_match:
                filtered_data = calc_data

        # Display columns - exclude Job Family and Job Description
        display_columns = [col for col in filtered_data.columns if col not in ["Job Family", "Job Description"]]

        # Status message placeholder for notifications
        status_message = st.empty()

        # Put all buttons in a single row at the top (before the data display)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            # Select All button
            if st.button("Select All" if not st.session_state.select_all else "Deselect All"):
                # Toggle select all state
                st.session_state.select_all = not st.session_state.select_all
                if st.session_state.select_all:
                    st.session_state.selected_rows = filtered_data["Job Code"].tolist()
                else:
                    st.session_state.selected_rows = []

                # Show selection count in the status message
                if st.session_state.select_all:
                    status_message.info(f"{len(filtered_data)} rows selected")
                else:
                    status_message.info("No rows selected")

                # Force rerun to update checkboxes
                st.rerun()


        # Replace the current Export buttons code with this improved version
        with col2:
            # Export Selected Data button with direct download
            if st.button("Export Selected Data"):
                # Check if any rows are selected
                if st.session_state.selected_rows:
                    # Filter data to only include selected rows
                    selected_data = filtered_data[filtered_data["Job Code"].isin(st.session_state.selected_rows)]

                    # Create export CSV data
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    export_filename = f"salary_data_export_{timestamp}.csv"

                    # Generate CSV for direct download
                    csv_data = selected_data.to_csv(index=False).encode()
                    b64 = base64.b64encode(csv_data).decode()

                    # Create a hidden HTML component that triggers download immediately
                    download_link = f'''
                    <html>
                    <head>
                        <title>Download</title>
                        <script>
                        function download() {{
                            var a = document.createElement('a');
                            a.href = "data:file/csv;base64,{b64}";
                            a.download = "{export_filename}";
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        }}
                        // Execute download function as soon as this HTML is rendered
                        window.onload = download;
                        </script>
                    </head>
                    <body>
                        If the download doesn't start automatically, <a href="data:file/csv;base64,{b64}" download="{export_filename}">click here</a>.
                    </body>
                    </html>
                    '''
                    # Display the HTML component
                    components.html(download_link, height=0)

                    # Show success message in status
                    status_message.success(f"Exporting {len(selected_data)} rows")
                else:
                    # Show warning in status
                    status_message.warning("Please select at least one row to export")

        with col3:
            # Export All Data button with direct download
            if st.button("Export All Data"):
                # Create export CSV data
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                export_filename = f"salary_data_export_all_{timestamp}.csv"

                # Generate CSV for direct download
                csv_data = filtered_data.to_csv(index=False).encode()
                b64 = base64.b64encode(csv_data).decode()

                # Create a hidden HTML component that triggers download immediately
                download_link = f'''
                <html>
                <head>
                    <title>Download</title>
                    <script>
                    function download() {{
                        var a = document.createElement('a');
                        a.href = "data:file/csv;base64,{b64}";
                        a.download = "{export_filename}";
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                    }}
                    // Execute download function as soon as this HTML is rendered
                    window.onload = download;
                    </script>
                </head>
                <body>
                    If the download doesn't start automatically, <a href="data:file/csv;base64,{b64}" download="{export_filename}">click here</a>.
                </body>
                </html>
                '''
                # Display the HTML component
                components.html(download_link, height=0)

                # Show success message in status
                status_message.success(f"Exporting {len(filtered_data)} rows")

        # Now create a form just for the data display without the duplicate buttons - USING UNIQUE KEY
        with st.form("data_view_form_benchmark"):  # CHANGED KEY HERE
            # Create a DataFrame for display with selection column
            display_df = filtered_data[display_columns].copy()

            # Convert numeric columns to strings to prevent type errors
            for col in display_df.columns:
                if display_df[col].dtype in [np.int64, np.float64]:
                    display_df[col] = display_df[col].astype(str)

            # Add selection column based on session state
            selection_column = [job_code in st.session_state.selected_rows for job_code in filtered_data["Job Code"]]
            display_df.insert(0, "Select", selection_column)

            # Display the data editor without a "Select All" checkbox (since we have one in the buttons)
            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                height=400,
                hide_index=True,
                column_config={
                    "Select": st.column_config.CheckboxColumn("Select", help="Select rows to export")
                },
                disabled=[col for col in display_df.columns if col != "Select"],
                key="unified_data_editor"
            )

            # Add a hidden submit button (required for forms)
            st.form_submit_button("Apply Selection", type="primary")

        # Process the data editor results (outside the form)
        if edited_df is not None:
            # Process the selections
            new_selected_rows = []
            for i, row in edited_df.iterrows():
                if row["Select"] and i < len(filtered_data):
                    job_code = filtered_data.iloc[i]["Job Code"]
                    new_selected_rows.append(job_code)

            # Update session state if selections changed
            if set(new_selected_rows) != set(st.session_state.selected_rows):
                st.session_state.selected_rows = new_selected_rows

                # Update select all state
                st.session_state.select_all = (len(new_selected_rows) == len(filtered_data) and len(filtered_data) > 0)

                # Show selection count
                if st.session_state.selected_rows:
                    status_message.info(f"{len(st.session_state.selected_rows)} rows selected")

    else:
        st.info("No benchmark data available. Please upload a file.")




# Part 5 #####################################
# - Job Descriptions Tab

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

    # Display success message if a save was just completed
    if st.session_state.last_successful_save:
        st.success("Job descriptions updated successfully!")
        # Reset the flag after displaying
        st.session_state.last_successful_save = False

    # Search Panel form for Job Descriptions - USING UNIQUE KEY
    with st.form(key="search_form_jobs"):  # CHANGED KEY HERE
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
            display_df['Job Code'] = display_df['Job Code'].astype(str)
            display_df['Job Title'] = display_df['Job Title'].astype(str)

            # Create a unique key for the data editor to force it to reset after saving
            editor_key = f"job_descriptions_data_editor_{id(st.session_state.benchmark_data)}"
            if st.session_state.last_successful_save:
                editor_key = f"job_descriptions_data_editor_after_save_{datetime.datetime.now().timestamp()}"

            # Modified to make all fields disabled/non-editable
            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                num_rows="fixed",
                height=400,
                column_config={
                    "Job Code": st.column_config.TextColumn("Job Code", disabled=True),
                    "Job Title": st.column_config.TextColumn("Job Title", disabled=True),
                    "Job Family": st.column_config.TextColumn("Job Family", disabled=True),
                    "Job Description": st.column_config.TextColumn("Job Description", width="large", disabled=True)
                },
                hide_index=True,
                key=editor_key,
                disabled=True  # Disable the entire data editor
            )

            # Check for changes between the original and edited dataframes - we keep this code
            # even though editing is disabled temporarily
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

            # Buttons at the bottom - removed since editing is temporarily disabled
            job_col1, job_col2, job_col3 = st.columns([3, 1, 1])

            with job_col3:
                # Display a disabled Save Changes button with a note that editing is temporarily disabled
                st.button("Save Changes", disabled=True, key="save_disabled_button")
                st.markdown(
                    '<div style="font-size:0.8rem; color:#d32f2f;">Editing is temporarily disabled.</div>',
                    unsafe_allow_html=True
                )
        else:
            missing_cols = [col for col in job_desc_columns if col not in st.session_state.benchmark_data.columns]
            st.error(f"Missing required columns in benchmark data: {', '.join(missing_cols)}")
    else:
        st.info("No benchmark data available. Please upload a file.")





# Part 6 ######################################################
# - Administration Tab
with tab3:
    st.markdown(
        '<div style="text-align:center; font-weight:bold; background-color:#f5f5f5; padding:5px; border:1px solid #ddd; border-radius:5px;">Administration</div>',
        unsafe_allow_html=True)

    st.write("### Data Management")

    # Admin Authentication
    if not st.session_state.admin_authenticated:
        with st.form("admin_auth_form"):  # Unique form key
            st.markdown("#### Administrator Access")
            st.write("Enter the administrator password to access data management features.")

            # Password input
            password = st.text_input("Password", type="password", key="password_input")

            # Submit button
            submit = st.form_submit_button("Login")

            if submit:
                verify_admin_password()

    # Admin Panel (shown only after authentication)
    if st.session_state.admin_authenticated:
        st.success("Administrator authenticated successfully")

        st.markdown("### Data Management Tools")

        # Direct Google Sheets access
        with st.form(key="db_access_form"):  # Unique form key
            st.write("#### Direct Database Access")
            st.write("Click the button below to open the Google Sheet database directly in a new tab.")

            sheet_url = open_google_sheet()
            if sheet_url:
                st.markdown(f"[Open Google Sheet Database]({sheet_url})", unsafe_allow_html=True)

            # Submit button
            st.form_submit_button("Open Database")

        # Data upload explanation
        with st.form(key="data_upload_form"):  # Unique form key
            st.write("#### Data Upload Instructions")
            st.write("""
            To update the database:
            1. Click the link above to open the Google Sheet
            2. Make your changes directly in the Google Sheet
            3. All changes are saved automatically
            4. The app will reflect the updated data on next load or refresh

            **Important Notes:**
            - Do not delete or rename the 'MainDatabase' worksheet
            - Keep the column headers intact
            - You can add or remove rows as needed
            - Format date fields as MM/DD/YYYY
            """)

            # Submit button
            st.form_submit_button("I Understand")

        # User access management
        with st.form(key="access_management_form"):  # Unique form key
            st.write("#### User Access Management")
            st.write("""
            To control who can access this tool:
            1. Share the Streamlit app URL only with authorized users
            2. For database editing privileges:
                - Open the Google Sheet database
                - Click the 'Share' button in the top-right corner
                - Add user emails and set appropriate permissions
                - Choose 'Editor' for users who should be able to modify data
                - Choose 'Viewer' for users who should only be able to view data

            The administrator password for this tool is separate from Google account access.
            """)

            # Add a submit button
            st.form_submit_button("Acknowledge")

        # Data storage information
        with st.form(key="data_storage_form"):  # Unique form key
            st.write("#### Data Storage Information")
            st.write("""
            **Where is my data stored?**
            - All data is stored in Google Sheets
            - This provides reliability, backup, and version history
            - Your data remains accessible even if this tool experiences temporary issues

            **Backup Recommendations:**
            - Periodically export data using the 'Export All Data' button in the Benchmark tab
            - Consider setting up automatic backups of the Google Sheet using Google Apps Script
            - For critical data, maintain a separate backup in another location
            """)

            # Add a submit button
            st.form_submit_button("I Understand")

        # Reset admin session
        with st.form(key="logout_form"):  # Unique form key
            st.write("#### Administrator Session")
            st.write("Click the button below to end your administrator session.")

            # Add a submit button for logout
            logout_button = st.form_submit_button("Logout")

            if logout_button:
                st.session_state.admin_authenticated = False
                st.rerun()

    # Help information
    with st.form(key="help_form"):  # Unique form key
        st.write("### Help")
        st.write("""
        **Troubleshooting:**
        - If the tool is not loading data, verify that the Google Sheet is accessible
        - For calculation issues, check that your input values are in the correct format
        - Date formats should be MM/DD/YYYY
        - Numeric values should not include currency symbols or commas

        **Support Contact:**
        For assistance, contact your administrator or IT support team.
        """)

        # Add submit button
        st.form_submit_button("Got It")
