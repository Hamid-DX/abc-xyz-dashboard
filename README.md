# ABC-XYZ Analysis Dashboard

A Streamlit dashboard for analyzing inventory data using ABC-XYZ analysis methodology.

## Features

- Secure authentication system
- Data upload capabilities
- Interactive ABC-XYZ matrix visualization
- Revenue analysis by territory and segment
- Inventory details with margin information

## Project Structure

```
abc_xyz_dashboard/
├── app.py                 # Main application entry point
├── authentication.py      # Authentication related functions
├── data_handler.py        # Data loading, validation and processing
├── visualizations.py      # Chart creation and data visualization
├── utils.py               # Utility functions
├── config.yaml            # User configuration (for development)
├── generate_password_hash.py  # Password utility
├── Dockerfile             # Docker configuration
├── docker-compose.yaml    # Docker Compose configuration
└── requirements.txt       # Python dependencies
```

## Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   streamlit run app.py
   ```

## Using Docker

```bash
docker-compose up -d
```

This will build and start the container with the dashboard available at http://localhost:8501.

## Data Requirements

The uploaded CSV file must contain the following columns:
- `ABC(Rev-Mar)`: ABC classification based on revenue or margin
- `Territory_XYZ`: XYZ classification for a specific territory
- `Inventory Name`: Name of inventory item
- `Territory`: Geographic territory
- `Total_revenue`: Revenue figures
- `Product_Margin`: Margin percentage (optional)

## Generating New Password Hashes

Use the included utility to generate secure password hashes:

```bash
python generate_password_hash.py
```

## Deployment

For Streamlit Cloud deployment, add your user credentials to the Streamlit secrets management system.

## Security Notes

- Passwords are stored as SHA-256 hashes
- User configuration is stored in `config.yaml` for development
- For production, use Streamlit's secrets management