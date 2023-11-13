import functions_framework
from enums import CATEGORIES
from pymongo import MongoClient
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

MONGO_CONNECTION_STRING = os.getenv("MONGODB_URL")
LEETCODE_API_URL = "https://leetcode.com/graphql"


def get_question_description(titleSlug):
    resp = requests.get(LEETCODE_API_URL, json={"query": "\n    query questionContent($titleSlug: String!) {\n  question(titleSlug: $titleSlug) {\n    content\n    mysqlSchemas\n    dataSchemas\n  }\n}\n    ", "variables": {
                        "titleSlug": titleSlug}, "operationName": "questionContent"})
    data = resp.json()
    return data["data"]["question"]["content"]


def get_all_questions(limit):
    resp = requests.get(LEETCODE_API_URL, json={"query": "query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {\n  problemsetQuestionList: questionList(\n    categorySlug: $categorySlug\n    limit: $limit\n    skip: $skip\n    filters: $filters\n  ) {\n    total: totalNum\n    questions: data {\n      acRate\n      difficulty\n      freqBar\n      frontendQuestionId: questionFrontendId\n      isFavor\n      paidOnly: isPaidOnly\n      status\n      title\n      titleSlug\n      topicTags {\n        name\n        id\n        slug\n      }\n      hasSolution\n      hasVideoSolution\n    }\n  }\n}", "variables": {"categorySlug": "", "skip": 0, "limit": limit, "filters": {}}})
    data = resp.json()["data"]["problemsetQuestionList"]["questions"]
    processed = []
    for question in data:
        question_categories = [tag["name"] for tag in question["topicTags"]]
        common_categories = set(question_categories) & set(CATEGORIES)
        if question["paidOnly"]:
            continue
        if common_categories:
            current = {}
            current["id"] = int(question["frontendQuestionId"])
            current["title"] = question["title"]
            current["categories"] = list(common_categories)
            current["complexity"] = question["difficulty"]
            current["link"] = "https://leetcode.com/problems/" + \
                question["titleSlug"]
            current["description"] = get_question_description(
                question["titleSlug"])
            processed.append(current)
    return processed


def populate_with_limit(limit):
    questions = get_all_questions(limit)

    myclient = MongoClient(MONGO_CONNECTION_STRING)

    db = myclient["test"]
    counter_collection = db["counters"]
    question_collection = db["questions"]
    question_collection.delete_many({})
    
    question_inserts = []
    for index, question in enumerate(questions):
        # Generate a new unique ID for each question
        question["id"] = 1 + index

        # Create a document to insert into the questions collection
        question_doc = {
            "id": question["id"],
            "title": question["title"],
            "categories": question["categories"],
            "complexity": question["complexity"],
            "link": question["link"],
            "description": question["description"],
        }

        # Append the question document to the questions collection
        question_inserts.append(question_doc)

    # Bulk insert the questions into the questions collection
    question_collection.insert_many(question_inserts)

    # Increment the counter by the number of questions
    counter_collection.find_one_and_update(
        {"name": "questionID"},
        {"$set": {"value": len(questions)}},
        upsert=True,
        return_document=True
    )

    return questions


@functions_framework.http
def scrape_leetcode(request):
    request_args = request.args
    if request_args and 'limit' in request_args:
        limit = request_args['limit']
    else:
        limit = 1000
    questions = populate_with_limit(limit)

    return 'peerprep db populated with {} questions'.format(len(questions))


if __name__ == "__main__":
    limit = 1000 if len(sys.argv) == 1 else int(sys.argv[1])
    populate_with_limit(limit)