from neo4j import GraphDatabase
import json
import os
from transformers import AutoTokenizer, AutoModel
import torch
import heapq

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4F_PASSWORD")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def query_db(transaction, symptom:str):
    result = transaction.run("""
        MATCH (n:Node)
        WHERE toLower(n.descriptions) CONTAINS $symptom
        OPTIONAL MATCH (n)-[r*1]-(m:Node)
        RETURN n.descriptions AS NodeDescription, m.descriptions AS RelatedNodeDescription, r AS relationship
    """, symptom=symptom.lower())

    return result

def compute_embeddings(tokenizer, model, item:str):
    # Initial encoding
    raw_input = tokenizer.encode(item, return_tensor="pt", truncation=True)

    # Turn off gradient updating
    with torch.no_grad:
        outputs = model(raw_input)

    # Return only embeddings
    return outputs.last_hidden_state[:, 0, :].squeeze()


def lambda_handler(event, context):
    """
    Main handler for sending queries and recieving results.
    """

    # Models
    tk = AutoTokenizer.from_pretrained("medicalai/ClinicalBERT")
    ml = AutoModel.from_pretrained("medicalai/ClinicalBERT")
    cos_diff = torch.nn.CosineSimilarity()

    # Constants
    PER_SYMPTOM = 3

    symptoms = event.get("symptoms", [])
    if not symptoms:
        return {"statusCode": 400, "body": json.dumps({"error": "No symptoms provided."})}
    
    global_best = []

    # Connect with Neo4j
    with driver.session() as session:

        # for each symptom provided by the user
        for symptom in symptoms:

            # Encoded the symptom provided by the user
            symptom_en = compute_embeddings(tk, ml, symptom)
            results = session.execute_read(query_db, symptom)

            # Top-k elements per each symptom
            local_best = []
            
            # Go through each row we get back and encode it
            for row in results:
                nodeDescription, relatedNode, relationship = row

                related_en = compute_embeddings(tk, ml, relatedNode)
                score = cos_diff(symptom_en, related_en)

                if len(local_best) >= PER_SYMPTOM:
                    heapq.heappush(local_best, (score, relatedNode))
                else:
                    # If it is lower than the lowest value then we change
                    if score > local_best[0][0]:
                        heapq.heapreplace(local_best, (score, relatedNode))

                        # Make sure it is properly sorted
                        heapq.heapify(local_best)

            sorted_reverse_best = sorted(local_best, key=lambda x: x[0], reverse=True)
            global_best.append(sorted_reverse_best)


    return {"statusCode": 200, "body": json.dumps({"diseases": "idk", "treatments": "dunno"})}
                    