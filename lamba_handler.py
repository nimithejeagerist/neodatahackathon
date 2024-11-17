from neo4j import GraphDatabase
import json
import os

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4F_PASSWORD")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def query(transaction, symptom:str):
    result = transaction.run("""
        MATCH (n:Node)
        WHERE toLower(n.descriptions) CONTAINS $symptom
        OPTIONAL MATCH (n)-[r*1]-(m:Node)
        RETURN n.descriptions AS NodeDescription, m.descriptions AS RelatedNodeDescription, r AS relationship
    """, symptom=symptom.lower())

    return result

def lambda_handler(event, context):
    symptoms = event.get("symptoms", [])
    if not symptoms:
        return {"statusCode": 400, "body": json.dumps({"error": "No symptoms provided."})}
    
    diseases = []
    treatments = []
    
    with driver.session() as session:
        for symptom in symptoms:
            results = session.execute_read(query, symptom)
            
            for record in results:
                disease = record["disease"]
                treatment = record["treatment"]
                
                if disease not in diseases:
                    diseases.append(disease)
                if disease not in treatments:
                    treatments[disease] = []

                if treatment and treatment not in treatments[disease]:
                    treatments[disease].append(treatment)

    return {"statusCode": 200, "body": json.dumps({"diseases": diseases, "treatments": treatments})}
                    