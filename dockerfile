FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt jupyter notebook ipython ipykernel

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Start a bash shell when the container runs
CMD ["/bin/bash"]