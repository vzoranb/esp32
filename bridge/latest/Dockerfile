FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install pyserial paho-mqtt

# Copy script
COPY bridge.py .

# Run the script
CMD ["python", "-u", "bridge.py"]
