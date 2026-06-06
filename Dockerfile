# Use a lightweight Python 3.14 base image
FROM python:3.14-slim  
# Disable writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED=1  
# Set working directory inside the container
WORKDIR /app  
# Install build tools, then clean apt cache
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*  
# Copy dependency list first for better Docker layer caching
COPY requirements.txt .  
# Install Python dependencies without cache
RUN pip install --no-cache-dir -r requirements.txt
# Copy application source code into the container
COPY . .  
# Create persistent data directories used by the app
RUN mkdir -p data/seeds  
RUN mkdir -p data/vector_store
RUN mkdir -p data/bm25
# Expose the app port and Streamlit port
EXPOSE 8000  
EXPOSE 8501
# Start the ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]