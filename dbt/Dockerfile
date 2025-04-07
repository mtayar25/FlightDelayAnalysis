# Use the official dbt-bigquery image
FROM ghcr.io/dbt-labs/dbt-bigquery:1.3.latest

# Set working directory inside the container
WORKDIR /app

# Copy dbt project files into the container
COPY . .

# Install any additional Python dependencies if needed (optional)
RUN pip install --no-cache-dir pandas

# Default command to run dbt commands inside the container
CMD ["dbt", "--help"]
