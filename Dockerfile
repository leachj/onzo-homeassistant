# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory to /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
  libudev-dev \
  libusb-1.0-0-dev

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Run app.py when the container launches
CMD python main.py
