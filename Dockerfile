FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p database

EXPOSE 5000

CMD ["python", "-c", "import app; app.create_tables(); app.app.run(host='0.0.0.0', port=5000, debug=False)"]