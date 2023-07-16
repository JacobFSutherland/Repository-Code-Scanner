# Repository-Code-Scanner
Automatically run SonarQube to get data about your repository for the last few quarters

# How to Run
## Step 1: Building the Scraper 
```docker build . -t scraper```

## Step 2:
Edit the docker-compose file and add the repository you want scraped in the `GIT_URL` environment variable, and how many quarters back you want with the `QUARTERS` environment variable.

## Step 3:
Wait for the scraper to finish running and access the dashboard with `localhost:9000` with the username: admin and password: admin
