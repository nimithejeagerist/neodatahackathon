import requests
import os

AWS_LAMBDA_URL = os.getenv("AWS_LAMBDA_URL")

def query_knowledge_graph(symptoms):
    payload = {"symptoms": symptoms}
    response = requests.post(AWS_LAMBDA_URL, json=payload)

    if response.status_code == 200:
        data = response.json()
        diseases = data.get("diseases", [])
        treatments = data.get("treatments", {})
        return diseases, treatments
    else:
        raise Exception(f"Error from AWS Lambda: {response.status_code}")