from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from retriever import query_knowledge_graph
from route import generate_response
from typing import List
import asyncio

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
    
    # Get answers asynchronously first, then use them for response generation
    answers = await query_knowledge_graph(symptoms)
    
    if not answers:
        raise HTTPException(status_code=404, detail="No relevant diseases found.")
    
    # Now generate the response using the obtained answers
    response = await generate_response(user_input, answers)
    
    return {"response": response}