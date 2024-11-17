from neo4j import GraphDatabase
import json
import os
from transformers import AutoTokenizer, AutoModel
import torch
import heapq

# Neo4j Credentials
# NEO4J_URI = os.getenv("NEO4J_URI")
# NEO4J_USER = os.getenv("NEO4J_USER")
# NEO4J_PASSWORD = os.getenv("NEO4F_PASSWORD")

# # Connection to Neo4j
# driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def query_db(transaction, symptom:str) -> list[list[str]]:
    """
    Send the query to the database
    """
    # Get every node that contains the word we're looking for or is one layer away from the node that contains we're looking for
    result = transaction.run("""
        MATCH (n:Node)
        WHERE toLower(n.descriptions) CONTAINS $symptom
        OPTIONAL MATCH (n)-[r*1]-(m:Node)
        RETURN n.descriptions AS NodeDescription, m.descriptions AS RelatedNodeDescription, r AS relationship
    """, symptom=symptom.lower())

    return result

def compute_embeddings(tokenizer, model, item:str) -> torch.tensor:
    """
    Get the embeddings of any string through the ClinicalBERT model
    """
    # Initial encoding
    raw_input = torch.tensor(tokenizer.encode(item, truncation="longest_first", max_length=512)).unsqueeze(0)

    # Turn off gradient updating
    with torch.no_grad():
        outputs = model(raw_input)

    # Return only embeddings
    return outputs.last_hidden_state[:, 0, :]


def lambda_handler():
    """
    Main handler for sending queries and recieving results.
    """

    # Models
    tk = AutoTokenizer.from_pretrained("medicalai/ClinicalBERT")
    ml = AutoModel.from_pretrained("medicalai/ClinicalBERT")
    cos_diff = torch.nn.CosineSimilarity()

    # Constants
    PER_SYMPTOM = 3
    PER_RESULT = 5

    # symptoms = event.get("symptoms", [])

    symptoms = ["cough", "covid-19", "runny nose"]

    if not symptoms:
        return {"statusCode": 400, "body": json.dumps({"error": "No symptoms provided."})}
    
    global_best = []
    unique_diseases = {}

    # Connect with Neo4j
    # with driver.session() as session:

        # for each symptom provided by the user
    for symptom in symptoms:

            # Encoded the symptom provided by the user
            symptom_en = compute_embeddings(tk, ml, symptom)
            # results = session.execute_read(query_db, symptom)
            results = [["sickness;cold;flu", "cough;sneeze;runny nose", "ATTRIBUTE"],
                    ["sickness;cold;flu", "covid-19;sars;bubonic plague", "ATTRIBUTE"],
                    ["sickness;cold;flu", "fever;headache;fatigue", "ATTRIBUTE"],
                    ["sickness;cold;flu", "sore throat;body aches;chills", "ATTRIBUTE"],
                    ["sickness;cold;flu", "bronchitis;pneumonia;sinus infection", "ATTRIBUTE"],
                    ["sickness;cold;flu", "nausea;vomiting;diarrhea", "ATTRIBUTE"],
                    ["sickness;cold;flu", "allergies;hay fever;asthma", "ATTRIBUTE"],
                    ["sickness;cold;flu", "conjunctivitis;ear infection;mononucleosis", "ATTRIBUTE"]]


            # Top-k elements per each symptom
            local_best = []

            # Turn it into a heap
            heapq.heapify(local_best)
            
            # Go through each row we get back and encode it
            for row in results:
                nodeDescription, relatedNode, relationship = row

                # Get embeddings of the related nodes to the node we found
                related_en = compute_embeddings(tk, ml, relatedNode)

                # Compute score with query and related nodes
                score = cos_diff(symptom_en, related_en)

                # If the list is not full then add it regardless
                if len(local_best) <= PER_SYMPTOM:
                    # Simply push it
                    heapq.heappush(local_best, (score, relatedNode))

                    # Make sure it is properly sorted
                    heapq.heapify(local_best)

                else:
                    # If it is lower than the lowest value then we change
                    if score > local_best[0][0]:
                        # Replace it with the lowest element
                        heapq.heapreplace(local_best, (score, relatedNode))

                        heapq.heapify(local_best)
            
            # Sort local best in a descending fashion
            local_reverse_best = sorted(local_best, key=lambda x: x[0], reverse=True)

            # Add it to global best
            # global_best.append(sorted_reverse_best[:PER_SYMPTOM])
            global_best.extend(local_reverse_best)

            for score, disease in local_reverse_best:
                # if disease already there then skip to next best scored disease
                if disease in unique_diseases:
                    continue
                # if disease not in unique_disease then add it
                elif disease not in unique_diseases and len(unique_diseases) < PER_RESULT:
                    unique_diseases[disease] = (score, disease)
                else:
                    # Remove the disease with the lowest score
                    lowest_score_disease = min(unique_diseases, key=lambda x: unique_diseases[x][0])
                    del unique_diseases[lowest_score_disease]
                    
                    # Add new disease
                    unique_diseases[disease] = (score, disease)
            
    global_best = sorted(unique_diseases.values(), key=lambda x: x[0], reverse=True)[:PER_RESULT]

    return {"statusCode": 200, "body": json.dumps({"diseases": "idk", "treatments": "dunno"})}


lambda_handler()