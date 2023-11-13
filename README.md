[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/UxpU_KWG)

# ServerlessTemplate

This repository houses the serverless function that is deploy on google functions in GCP.

## Local testing and general info
- The serverless function takes in http requests and scrapes leetcode to populate the peerprep question database.
- The serverless function fetches the questions in leetcode in order, and based on the categories we want to scrape (found in enums) we can populate the question repo 
based on the intersection of the original question's categories and the enums defined by the team.
- whenever the serverless function is invoked, the question repo is first wiped clean, before populating the question database
- For testing, ensure that a small limit is defined, preferably 30 questions at the start, if you do not want long waiting times.


## Local Set Up
- ensure you are in the project directory and you have python 3.12 installed
- To setup dependencies, please run

```
pip3 install -r requirements.txt
```

- To run serverless function run 

```
python3 main.py <limit>
```
- this will scrape the first <limit> questions of leetcode into the question db given that the questions have matching categories with the enums.
- For example, `python3 main.py 10` would reset the database with the first 10 questions from leetcode.

## Deployed serverless cloud function
- To run the serverless function without any setup, function is deployed into google cloud functions.
- Visit (https://us-central1-serverless-peerprep.cloudfunctions.net/populate_ques_peerprep?limit=30) to invoke the function from the cloud and feel free to change the limit.


### viewing the results (deployed frontend)

The easiest way to view the results is to go to our [deployed frontend](http://g15-peerprep.ap-southeast-1.elasticbeanstalk.com/) and signup and login accordingly






