# ABC-XYZ Analysis Dashboard - Docker Setup

This README provides instructions for setting up and running the ABC-XYZ Analysis Dashboard in a Docker container.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)

## Files Structure

Ensure your project directory has the following structure:

```
abc_xyz_dashboard/
├── app.py                 # Main application entry point
├── authentication.py      # Authentication related functions
├── data_handler.py        # Data loading, validation and processing
├── visualizations.py      # Chart creation and data visualization
├── utils.py               # Utility functions
├── config.yaml            # Config file (for development)
├── generate_password_hash.py  # Password utility
├── .streamlit/            # Streamlit configuration
│   └── secrets.toml       # (gitignored) Secrets for cloud deployment
├── Dockerfile             # Docker configuration
├── docker-compose.yaml    # Docker Compose configuration
└── requirements.txt       # Python dependencies
```

## Setup Instructions

### 1. Prepare Your Data

- Place your `full__abc_xyz.csv` file in the `data/` directory

### 2. Building and Running the Docker Container

#### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# Connect to the container
docker exec -it abc-xyz-dashboard bash

# Once inside the container, run the application
streamlit run app.py
# OR for version without login
# streamlit run app_no_login.py
```

#### Using Docker Directly

```bash
# Build the Docker image
docker build -t abc-xyz-dashboard .

# Run the container
docker run -p 8501:8501 -v $(pwd)/data:/app/data -it abc-xyz-dashboard

# Once inside the container, run the application
streamlit run app.py
# OR for version without login
# streamlit run app_no_login.py
```

## Accessing the Application

- Open your web browser and navigate to `http://localhost:8501`

## Troubleshooting Authentication Issues

If you're experiencing authentication problems:

### 1. Verify Password Hashes

Use the `password_generator.py` script to generate new password hashes:

```bash
python password_generator.py
```

Update the hashes in `config.yaml` with the newly generated ones.

### 2. Check Configuration Format

Ensure your `config.yaml` follows this structure:

```yaml
credentials:
  usernames:
    admin:
      email: example@domain.com
      name: Admin User
      password: "$2b$12$..."  # Hashed password
    user1:
      email: user@domain.com
      name: Regular User
      password: "$2b$12$..."  # Hashed password

cookie:
  expiry_days: 30
  key: "random_signature_key"
  name: "cookie_name"

preauthorized:
  emails:
    - preauth@domain.com
```

### 3. Version Compatibility

The application is designed to work with `streamlit-authenticator==0.1.5`. If you're using a different version, you may need to adjust the authentication code accordingly.

### 4. Use App Without Login for Testing

If you continue to experience login issues, you can run `app_no_login.py` to test the application functionality without authentication:

```bash
streamlit run app_no_login.py
```

This will help isolate whether the problem is with the authentication system or the underlying application.