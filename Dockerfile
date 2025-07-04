FROM python:3.9-slim-buster

WORKDIR /app

# Install dependencies (replace with your requirements file)
COPY .env .
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# Define the command to run the app (replace with your entrypoint)
CMD [ "python", "app.py" ]
