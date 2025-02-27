# Salary Survey Tool

A Streamlit web application for analyzing and visualizing salary benchmark data with Google Sheets integration.

## Features

- **Search and Filter**: Easily find salary benchmarks by job title, industry, or geographic location
- **Dynamic Calculations**: Apply adjustments for security clearance, special skills, and geographic differentials
- **Job Descriptions Management**: Edit and manage job descriptions directly in the application
- **Data Export**: Export filtered data to CSV format for further analysis
- **Google Sheets Integration**: Seamless integration with Google Sheets for data storage

## Technology Stack

- **Frontend & Backend**: Streamlit
- **Data Processing**: Pandas
- **Data Storage**: Google Sheets API
- **Authentication**: Google Cloud Service Account

## Deployment

This application is deployed using [Streamlit Cloud](https://streamlit.io/cloud).

## Local Development

If you want to run this application locally:

1. Clone this repository
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Set up your Google Sheets API credentials in a `.streamlit/secrets.toml` file
4. Run the application:
   ```
   streamlit run streamlit_app.py
   ```

## Security Note

This application uses Google Sheets API for data storage. Credentials are managed securely through Streamlit's secrets management and are not included in the source code.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the amazing app framework
- [Google Sheets API](https://developers.google.com/sheets/api) for data storage capabilities
