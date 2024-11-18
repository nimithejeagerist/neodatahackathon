from neo4j import GraphDatabase
import json
import os
from transformers import AutoTokenizer, AutoModel
import torch
import heapq
import streamlit as st
import ssl


# Neo4j Credentials
NEO4J_URI = st.secrets["neo4j"]["uri"]
NEO4J_USER = st.secrets["neo4j"]["user"]
NEO4J_PASSWORD = st.secrets["neo4j"]["password"]

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def query_db(transaction, symptom:str) -> list[list[str]]:
    """
    Send the query to the database
    """
    # Get every node that contains the word we're looking for or is one layer away from the node that contains we're looking for
    result = transaction.run("""
        MATCH (n:Nodes)
        WHERE toLower(n.descriptions) CONTAINS $symptom
        OPTIONAL MATCH (n)-[r*1..2]-(m:Nodes)
        RETURN DISTINCT n.descriptions AS NodeDescription, m.descriptions AS RelatedNodeDescription, r AS relationship
        LIMIT 100
    """, symptom=symptom.lower())

    return [record for record in result]

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


def query_knowledge_graph(symptoms:list):
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
    
    global_best = []
    unique_diseases = {}

    # If symptoms is empty then exit and return 1 as a error code
    if not symptoms:
        return 1

    # Connect with Neo4j
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD), ssl_context=ssl_context) as driver:
        driver.verify_connectivity()

        # for each symptom provided by the user
        for symptom in symptoms:

            # Encoded the symptom provided by the user
            symptom_en = compute_embeddings(tk, ml, symptom)

            # Connect to the driver
            with driver.session() as session:
                results = session.execute_read(query_db, symptom)

            # Top-k elements per each symptom
            local_best = []

            # Turn it into a heap
            heapq.heapify(local_best)
            
            # Go through each row we get back and encode it
            for row in results:
                relatedNode = row["RelatedNodeDescription"]
                
                if not isinstance(relatedNode, str):
                    continue

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
            global_best.extend(local_reverse_best)

            for score, disease in local_reverse_best:
                # if disease already there then skip to next best scored disease
                if disease in unique_diseases:
                    continue
                # if disease not in unique_disease then add it
                elif disease not in unique_diseases and len(unique_diseases) < PER_RESULT:
                    unique_diseases[disease] = (score, disease)
                else:
                    # Find the disease with the lowest score
                    lowest_score_disease = min(unique_diseases, key=lambda x: unique_diseases[x][0])

                    # remove that disease
                    del unique_diseases[lowest_score_disease]
                    
                    # Add new disease
                    unique_diseases[disease] = (score, disease)

    # Sort global_best and return required values
    global_best = sorted(unique_diseases.values(), key=lambda x: x[0], reverse=True)[:PER_RESULT]
    
    important_results = []
    for tenor, word in  global_best:
        important_results.append(word) 

    return important_results

