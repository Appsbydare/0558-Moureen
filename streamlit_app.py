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

    /* Make tabs look like the desktop app */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        font-weight:bold;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 6px 36px;
        font-weight:bold;
        border: 1px solid #ddd;
        border-bottom: none;
        border-radius: 4px 4px 0 0;
    }

    /* Change tabs highlight color from red to green */
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #2E8B57 !important;
        font-weight: bold;
    }

    /* Change underline of selected tab to green */
    .stTabs [aria-selected="true"]::before {
        background-color: #2E8B57 !important;
    }

    /* Remove Streamlit's element margins */
    div.element-container {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Standard Button Styling - White with Black Text */
    .grey-button, 
    button[kind="primary"],
    button[kind="secondary"],
    div.stButton > button {
        background-color: #E6EAE9 !important;
        color: black !important;
        border: 1px solid #D3DBD8 !important;
        border-radius: 16px !important;
        padding: 0px 20px !important;
        cursor: pointer !important;
        box-shadow: 4px 4px 5px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
    }

    /* Button Hover Effects - Green Background with White Text */
    .grey-button:hover,
    button[kind="primary"]:hover,
    button[kind="secondary"]:hover,
    div.stButton > button:hover {
        background-color: #2E8B57 !important;
        color: white !important;
        border-color: #2E8B57 !important;
    }

    /* Primary Button Styling - White with Black Text */
    div.stButton > button[data-baseweb="button"][kind="primary"] {
        background-color: white !important;
        color: black !important;
        border: 1px solid #2E8B57 !important;
    }

    div.stButton > button[data-baseweb="button"][kind="primary"]:hover {
        background-color: #2E8B57 !important;
        color: white !important;
        border-color: #2E8B57 !important;
    }

    /* Disabled button styling */
    div.stButton > button:disabled {
        background-color: #f0f0f0 !important;
        color: #888 !important;
        cursor: not-allowed !important;
        border: 1px solid #ccc !important;
    }

    /* Main title */
    .main-title {
        text-align: center;
        font-size: 24px;
        font-family: Impact;
        margin:2px 0;
    }

    /* Container for the whole application */
    .app-container {
        margin: 0 auto;
        width: 100%;
    }

    /* Improved scrollbar styling - only change thickness */
    [data-testid="stDataFrame"] div::-webkit-scrollbar {
        height: 15px !important;
    }

    [data-testid="stDataFrame"] div::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 5px;
    }

    /* Success message styling inside form - change to green */
    .success-message {
        color: #2E8B57;
        font-size: 14px;
        font-weight: bold;
        padding: 5px;
        margin: 5px 0;
        text-align: center;
    }

    /* Error message styling inside form */
    .error-message {
        color: red;
        font-size: 14px;
        font-weight: bold;
        padding: 5px;
        margin: 5px 0;
        text-align: center;
    }

    /* Adjust form button width/positioning for compact layout */
    div.stButton > button.stFormSubmitter {
        width: 100%;
        padding: 0.375rem 0.5rem;
        font-size: 0.9rem;
    }

    /* Ensure the dropdown menus are smaller and match other elements */
    .stSelectbox > div > div {
        min-height: 16px !important;
    }

    /* Make date picker more compact */
    .stDateInput > div > div {
        min-height: 16px !important;
    }

    /* Make number input elements more compact */
    .stNumberInput > div {
        flex-direction: row;
        align-items: center;
    }

    /* Adjust the input elements themselves */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stDateInput > div > div > input {
        padding: 0.25rem 0.5rem !important;
        height: 30px !important;
        font-size: 0.9rem !important;
    }

    /* Reduce padding for form layout */
    div.stForm > div {
        padding: 0 !important;
    }

    /* Make form components tighter */
    div.stForm [data-testid="column"] {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }

    /* Ensure calculation panel labels don't wrap */
    .calculation-label {
        font-size: 0.85rem !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Change focus color for all controls from red to green */
    input:focus, 
    .stSelectbox [data-baseweb="select"] > div:focus,
    .stDateInput input:focus {
        border-color: #2E8B57 !important;
        box-shadow: 0 0 0 1px #2E8B57 !important;
    }

    /* Style the number input stepper buttons to use green */
    .stNumberInput button svg {
        fill: #2E8B57 !important;
    }

    /* Override the number input increase/decrease buttons - replace red with green */
    .stNumberInput [data-baseweb="spinner"] button {
        background-color: white !important;
        color: black !important;
        border: 1px solid #2E8B57 !important;
    }

    .stNumberInput [data-baseweb="spinner"] button:hover {
        background-color: #2E8B57 !important;
        color: white !important;
        border-color: #2E8B57 !important;
    }

    /* Fix the specific plus button */
    .stNumberInput button[aria-label="Increase"] {
        background-color: white !important;
        color: black !important;
        border: 1px solid #2E8B57 !important;
        border-radius: 0px;
    }

    .stNumberInput button[aria-label="Increase"]:hover {
        background-color: #2E8B57 !important;
        color: white !important;
        border-color: #2E8B57 !important;
    }

    /* Fix the minus button */
    .stNumberInput button[aria-label="Decrease"] {
        background-color: white !important;
        color: black !important;
        border: 1px solid #2E8B57 !important;
    }

    .stNumberInput button[aria-label="Decrease"]:hover {
        background-color: #2E8B57 !important;
        color: white !important;
        border-color: #2E8B57 !important;
    }

    /* Change success notification color */
    [data-testid="stNotification"] {
        background-color: #f0f8f0 !important;
        border-color: #2E8B57 !important;
    }

    /* Data editor styling for job descriptions tab */
    [data-testid="stDataEditor"] {
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f8f8f8;
        margin-bottom: 10px;
    }

    /* Dataframe styling - change selection color */
    [data-testid="stDataFrame"] [role="cell"]:focus {
        outline-color: #2E8B57 !important;
    }

    /* Target the tab indicator bar */
    .stTabs [role="tablist"] [data-testid="stHorizontalBlock"] {
        background-color: #2E8B57 !important;
    }

    /* Bottom action buttons */
    [data-testid="baseButton-secondary"] {
        background-color: white !important;
        color: black !important;
        border: 1px solid #2E8B57 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="baseButton-secondary"]:hover {
        background-color: #2E8B57 !important;
        color: white !important;
    }

    /* Ensure all buttons have consistent styling */
    button, 
    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px !important;
        background-color: #f5f5f5 !important;
        color: black !important;
        border: 1px solid #f8f8f8 !important;
    }

    button:hover, 
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background-color: #2BA903 !important;
        color: white !important;
        border-color: #30C103 !important;
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

            # Clear button in fifth column
            with clear_col:
                st.markdown('<div style="padding-top:2px;">&nbsp;</div>', unsafe_allow_html=True)
                clear_filters = st.form_submit_button("Clear")

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

    # Handle clear filters button click
    if clear_filters:
        # Set a flag to clear filters on next rerun
        st.session_state.clear_filters_clicked = True
        # Clear calculation status
        st.session_state.calc_success = False
        st.session_state.calc_error = ""
        st.rerun()

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
                    st.rerun()

        # Display download link if export was requested
        if st.session_state.display_download_link:
            b64 = base64.b64encode(st.session_state.export_csv).decode()
            download_href = f'<a href="data:file/csv;base64,{b64}" download="{st.session_state.export_filename}">Download CSV File</a>'
            st.markdown(download_href, unsafe_allow_html=True)
            st.success("Your data is ready for download")

            # Add a button to clear the download link
            if st.button("Clear Download"):
                st.session_state.display_download_link = False
                st.rerun()

        with col3:
            upload_button = st.button("Upload Data")
            if upload_button:
                st.session_state.show_upload = True

    else:
        st.info("No benchmark data available. Please upload a file.")

    # File uploader - Only show when needed
    if 'show_upload' not in st.session_state:
        st.session_state.show_upload = False

    if st.session_state.show_upload:
        with st.container():
            uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"],
                                             key="benchmark_uploader")

            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        new_data = pd.read_csv(uploaded_file)
                    else:
                        new_data = pd.read_excel(uploaded_file)

                    # Update the session state with new data
                    st.session_state.benchmark_data = new_data

                    # Save to Google Sheet
                    if save_data_to_google_sheet(new_data):
                        st.success(f"Successfully loaded and saved to Google Sheets")
                    else:
                        st.error("Failed to save data to Google Sheets")

                    st.session_state.show_upload = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Error loading file: {e}")
# Job Descriptions Tab
# Job Descriptions Tab
with tab2:
    # Helper function to reset job search filters
    def reset_job_search_filters():
        """Helper function to reset job search filters"""
        if 'job_code_search' in st.session_state:
            st.session_state.job_code_search = ""
        if 'job_title_search' in st.session_state:
            st.session_state.job_title_search = ""
        if 'job_family_search' in st.session_state:
            st.session_state.job_family_search = ""


    # Initialize session state for job descriptions if not already done
    if 'edited_rows' not in st.session_state:
        st.session_state.edited_rows = {}
    if 'save_needed' not in st.session_state:
        st.session_state.save_needed = False
    if 'clear_job_filters_clicked' not in st.session_state:
        st.session_state.clear_job_filters_clicked = False

    # Check if we need to handle a previous clear filters request
    if st.session_state.get('clear_job_filters_clicked', False):
        reset_job_search_filters()
        st.session_state.clear_job_filters_clicked = False

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

        # Clear button
        col1, col2 = st.columns([1, 1])
        with col1:
            clear_job_filters = st.form_submit_button("Clear Filters")

    # Handle clear filters button click
    if clear_job_filters:
        st.session_state.clear_job_filters_clicked = True
        st.rerun()

    # Filter job descriptions from benchmark data
    if not st.session_state.benchmark_data.empty:
        # Extract just the job description columns we need
        job_desc_columns = ["Job Code", "Job Title", "Job Family", "Job Description"]

        # Make sure all required columns exist
        if all(col in st.session_state.benchmark_data.columns for col in job_desc_columns):
            job_desc_filtered = st.session_state.benchmark_data[job_desc_columns].copy()

            # Apply filters
            if job_code_search:
                job_desc_filtered = job_desc_filtered[
                    job_desc_filtered["Job Code"].astype(str).str.contains(job_code_search, case=False, na=False)
                ]
            if job_title_search:
                job_desc_filtered = job_desc_filtered[
                    job_desc_filtered["Job Title"].astype(str).str.contains(job_title_search, case=False, na=False)
                ]
            if job_family_search:
                job_desc_filtered = job_desc_filtered[
                    job_desc_filtered["Job Family"].astype(str).str.contains(job_family_search, case=False, na=False)
                ]

            # Convert Job Family and Job Description to string before editing
            job_desc_filtered['Job Family'] = job_desc_filtered['Job Family'].astype(str)
            job_desc_filtered['Job Description'] = job_desc_filtered['Job Description'].astype(str)

            # Display filtered data with editable cells
            edited_df = st.data_editor(
                job_desc_filtered,
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

            # Check if data was edited and needs saving
            if edited_df is not None and not edited_df.equals(job_desc_filtered):
                st.session_state.edited_rows = edited_df
                st.session_state.save_needed = True

            # Buttons at the bottom
            job_col1, job_col2, job_col3 = st.columns([3, 1, 1])

            with job_col2:
                upload_job_button = st.button("Upload Data", key="upload_job_btn")
                if upload_job_button:
                    st.session_state.show_job_upload = True

            with job_col3:
                # Show save button only when changes need saving
                if st.session_state.save_needed:
                    save_button = st.button("Save Changes", type="primary")
                    if save_button:
                        try:
                            # Update the main benchmark dataframe with edited values
                            for index, row in st.session_state.edited_rows.iterrows():
                                # Find the corresponding index in the original dataframe
                                original_indices = st.session_state.benchmark_data.index[
                                    st.session_state.benchmark_data["Job Code"] == row["Job Code"]
                                    ].tolist()

                                if original_indices:
                                    # Update Job Family and Job Description
                                    st.session_state.benchmark_data.loc[
                                        original_indices[0], "Job Family"] = row["Job Family"]
                                    st.session_state.benchmark_data.loc[
                                        original_indices[0], "Job Description"] = row["Job Description"]

                            # Save to Google Sheets instead of local file
                            if save_data_to_google_sheet(st.session_state.benchmark_data):
                                st.success("Changes saved successfully to Google Sheets!")
                                st.session_state.save_needed = False
                                st.rerun()
                            else:
                                st.error("Failed to save changes to Google Sheets")
                        except Exception as e:
                            st.error(f"Error saving changes: {e}")
                else:
                    st.button("Save Changes", disabled=True)
        else:
            missing_cols = [col for col in job_desc_columns if col not in st.session_state.benchmark_data.columns]
            st.error(f"Missing required columns in benchmark data: {', '.join(missing_cols)}")
    else:
        st.info("No benchmark data available. Please upload a file.")

    # File uploader
    if 'show_job_upload' not in st.session_state:
        st.session_state.show_job_upload = False

    if st.session_state.show_job_upload:
        with st.container():
            job_desc_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"],
                                             key="job_desc_uploader")

            if job_desc_file is not None:
                try:
                    if job_desc_file.name.endswith('.csv'):
                        uploaded_data = pd.read_csv(job_desc_file)
                    else:
                        uploaded_data = pd.read_excel(job_desc_file)

                    # Check if the uploaded file has the required columns
                    required_cols = ["Job Code", "Job Title", "Job Family", "Job Description"]
                    if all(col in uploaded_data.columns for col in required_cols):
                        # Update only the Job Family and Job Description columns in benchmark_data
                        for index, row in uploaded_data.iterrows():
                            # Find if this Job Code already exists in benchmark_data
                            match_idx = st.session_state.benchmark_data.index[
                                st.session_state.benchmark_data["Job Code"] == row["Job Code"]
                                ].tolist()

                            if match_idx:
                                # Update existing row
                                st.session_state.benchmark_data.loc[match_idx[0], "Job Family"] = row["Job Family"]
                                st.session_state.benchmark_data.loc[match_idx[0], "Job Description"] = row[
                                    "Job Description"]
                            else:
                                # This is a new job code, we need to add it to benchmark_data with minimal info
                                new_row = pd.DataFrame({
                                    "Job Code": [row["Job Code"]],
                                    "Job Title": [row["Job Title"]],
                                    "Job Family": [row["Job Family"]],
                                    "Job Description": [row["Job Description"]]
                                })
                                # Add other required columns with empty/default values
                                for col in st.session_state.benchmark_data.columns:
                                    if col not in new_row.columns:
                                        new_row[col] = None

                                # Append to benchmark_data
                                st.session_state.benchmark_data = pd.concat([st.session_state.benchmark_data, new_row],
                                                                            ignore_index=True)

                        # Save to Google Sheets instead of local file
                        if save_data_to_google_sheet(st.session_state.benchmark_data):
                            st.success(f"Successfully loaded and saved to Google Sheets")
                        else:
                            st.error("Failed to save data to Google Sheets")

                        st.session_state.show_job_upload = False
                        st.rerun()
                    else:
                        st.error(
                            f"Uploaded file missing required columns: {', '.join([col for col in required_cols if col not in uploaded_data.columns])}")
                except Exception as e:
                    st.error(f"Error loading file: {e}")