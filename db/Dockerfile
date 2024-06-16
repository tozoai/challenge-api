# Use the official MongoDB image as the base image
FROM mongo:latest

# Set environment variables to configure MongoDB
ENV MONGO_INITDB_ROOT_USERNAME=mongouser
ENV MONGO_INITDB_ROOT_PASSWORD=mongopass
ENV MONGO_INITDB_DATABASE=data

# (Optional) Copy any custom scripts or datasets you want to initialize the database with
# COPY ./init-mongo.js /docker-entrypoint-initdb.d/

# Expose port 27017 to access MongoDB
EXPOSE 27017