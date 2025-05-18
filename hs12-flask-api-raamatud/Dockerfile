FROM python:3.8-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Tell Flask where your app lives
ENV FLASK_APP=hs12-flask-api-raamatud.py

EXPOSE 5000

# Start via flask run
CMD ["flask", "run", "--host=0.0.0.0"]
