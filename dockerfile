FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY config.yaml .
COPY password_generator.py .

# Create data directory and ensure permissions
# RUN mkdir -p /app/data
# RUN chmod 777 /app/data

# Expose Streamlit port
# EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start a bash shell when the container runs
CMD ["/bin/bash"]