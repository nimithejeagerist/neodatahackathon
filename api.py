from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from retriever import query_knowledge_graph
from route import generate_response
from typing import List

app = FastAPI()

class QueryRequest(BaseModel):
    symptoms: List[str]
    user_input: str

@app.get("/healthcheck")
def healthcheck():
    return {"status": "API is running"}

@app.post("/query")
async def handle_query(request: QueryRequest):
    symptoms = request.symptoms
    user_input = request.user_input
    
    print(symptoms)
    print(user_input)
    
    answers = query_knowledge_graph(symptoms)
    
    print(answers)
    
    if not answers:
        raise HTTPException(status_code=404, detail="No relevant diseases found.")
    
    response = generate_response(user_input, answers)
    print(response)
    return {"response": response}