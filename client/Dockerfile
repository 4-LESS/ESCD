FROM python:3.10-slim

WORKDIR /app

COPY client_str.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "client_str.py", "--server.headless=true", "--browser.gatherUsageStats=false"]
