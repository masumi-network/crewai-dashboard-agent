FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Create directories if they don't exist
RUN mkdir -p dashboards

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Start the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 