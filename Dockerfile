# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install discord.py
RUN pip install discord.py

# Run bot.py when the container launches
CMD ["python", "bot.py"]