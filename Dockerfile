FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/ ./src/
COPY 信用卡資料模板.csv .

# Create .env from environment variables at runtime
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Initialize vector database and start application
CMD cd src && python init_db.py && python main.py
