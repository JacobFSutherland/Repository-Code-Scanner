# Import necessary libraries for parsing JSON, handling date and time, interacting with the operating system and subprocesses
import json
import time
import datetime
import json
import subprocess
import os
import sys

# Mapping of quarter numbers to corresponding months
map = {
    1: 10,
    2: 1,
    3: 1,
    4: 4,
    5: 4,
    6: 4,
    7: 4,
    8: 7,
    9: 7,
    10: 7,
    11: 10,
    12: 10,
}

# Mapping of current quarter to the immediately preceding quarter
prevQuarter = {
    1: 10,
    10: 7,
    7: 4,
    4: 1,
}

# Get the current working directory
appPath = os.getcwd();

# A function to get all git hashes from the specific number of quarters
def getAllGitHashes(quarters):
    # The command to get the git main branch
    get_main_branch = ['git', 'symbolic-ref', '--short', 'HEAD']

    # List to store the hashes
    hashes = []
    # Clone the repository given in the GIT_URL environment variable to a 'data' directory
    subprocess.check_output(['git', 'clone', '--no-checkout' , os.getenv('GIT_URL'), 'data']).decode()
    # Change to the 'data' directory
    os.chdir('data')
    # Fetch all git objects
    subprocess.check_output(['git', 'fetch']).decode()
    # Get the current year
    year = datetime.date.today().year
    # Get the current quarter
    currentQuarter = map[datetime.date.today().month]
    # Get the main branch name
    main_branch = subprocess.check_output(get_main_branch).decode().strip()
    # Check out to that main branch
    subprocess.check_output(['git', 'checkout', main_branch]).decode()

    # If it's January, adjust the year to previous and the quarter to the previous quarter 
    if(datetime.date.today().month == 1):
        year = year-1
        currentQuarter = prevQuarter(currentQuarter)
    
    # Loop to get the git hashes from previous quarters
    while(quarters > 0):
        # Command to get git hash given the year and the quarter
        getHashAtTime = ['git', 'log', '-n', '1', '--pretty=format:%H' , f'--since={year}-{currentQuarter}-01' ,f'--until={year}-{currentQuarter+2}-30']
        # Get the hash
        commit_hash = subprocess.check_output(getHashAtTime).decode();
        # If the commit_hash is empty, reset the branch to main. This can happen if a new branch was cut after the commit of interest
        if(commit_hash == ''):
            main_branch = subprocess.check_output(get_main_branch).decode().strip()
            subprocess.check_output(["git", "reset", "--hard", main_branch]).decode()
            commit_hash = subprocess.check_output(getHashAtTime).decode();
        # Store the date and the hash
        commit_data = {"date": f'{year}-{currentQuarter}', 'hash': commit_hash}
        hashes.append(commit_data)
        # If the current quarter is 1, subtract a year
        if(currentQuarter == 1):
            year = year - 1

        # Move back a quarter
        currentQuarter = prevQuarter[currentQuarter]
        # Decrease the remaining quarters to process by one
        quarters = quarters -1

    # Return the list of hashes
    return hashes; 

# Run the SonarScanner on a specific git hash and returns the scan result
def runSonarScannerOnHash(hash):
    if(hash['hash'] == ''):
        return {}
    # Reset the git to the specific hash
    res = subprocess.check_output(['git', 'reset', '--hard', hash['hash']]).decode();
    print(res)
    # Change directory to the application path
    os.chdir(appPath) 
    # Run the Sonar scanner
    scanResults = run_sonar_scanner()
    # Change back to the data directory (where the git repository was cloned)
    os.chdir('data') 
    return scanResults

# Run the Sonar scanner and return the result
def run_sonar_scanner():
    url = f"http://sonarqube:9000/api/measures/component?component={os.getenv('KEY')}&metricKeys=code_smells,vulnerabilities,bugs"
    print(url)
 
    try:
        # Run Sonar scanner
        response = subprocess.check_output(['sonar-scanner']).decode()
        time.sleep(10)
        # Get the scanner results and parse the result
        results = subprocess.check_output(['curl', '-X', 'GET', '-u', 'admin:admin', url]).decode()
        print(f"Results: {results}")
        results = json.loads(results);
        dataset = {}
        # Create a dictionary with metric keys and their corresponding values
        for datapoint in results['component']['measures']:
            dataset[datapoint['metric']] = datapoint['value']
        return dataset;
    # Error handling for failed scanner execution
    except Exception as e:
        print(f"Error when running SonarScanner: {e}")

def main():
    hashes = getAllGitHashes(os.getenv('QUARTERS'))
    for commithash in hashes:
        # Run SonarScanner on each hash and save the result to the current hash dictionary
        result = runSonarScannerOnHash(commithash)
        commithash['result'] = result;
    print(hashes)

main()