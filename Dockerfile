from sonarsource/sonar-scanner-cli

# Set up working dir
WORKDIR /app

# Copy the helper.py and requirements.txt files to the working directory
COPY helper.py sonar-project.properties ./

# Install the dependencies from requirements.txt
ENV GIT_URL=${GIT_URL}
ENV QUARTERS+=${QUARTERS}

#Install git
RUN apk add git

# Run the python file
CMD ["python", "helper.py"]