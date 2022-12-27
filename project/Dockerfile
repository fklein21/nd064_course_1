# set the base image.
FROM python:3.8-slim

# set a key-value label for the Docker image
LABEL maintainer="Ferdinand Kleinschroth"

# copy the contents of the local directory into the container
COPY techtrends /app

#  Define the working directory within the container
WORKDIR /app

# Install dependencies defined in the requirements.txt file. 
RUN pip install -r requirements.txt
RUN python init_db.py

# Expose the port that the app is running on.
EXPOSE 3111

# Command to run on container start. 
CMD [ "python", "app.py" ]