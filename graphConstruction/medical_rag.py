# -*- coding: utf-8 -*-
import pandas as pd
from neo4j import GraphDatabase
from pathlib import Path
import csv


def colab_requirements():
  """
  Requirements for a Colab enviroment.
  """
  # !pip install neo4j
  # from google.colab import drive
  # drive.mount('/content/drive')
  nodes = Path("/content/drive/MyDrive/MedicalRAG/Nodes.txt")
  description = Path("/content/drive/MyDrive/MedicalRAG/Description.txt")
  relationships = Path("/content/drive/MyDrive/MedicalRAG/Relationships.txt")

  return nodes, description, relationships


def local_requirements():
  """
  Requirements for a local, personal enviroment
  """
  nodes = Path("/content/drive/MyDrive/MedicalRAG/Nodes.txt")
  description = Path("/content/drive/MyDrive/MedicalRAG/Description.txt")
  relationships = Path("/content/drive/MyDrive/MedicalRAG/Relationships.txt")

  return nodes, description, relationships


def to_csv(nodes, description, relationships):
  """
  Convert files to CSV and download them locally.
  """
  nodes.to_csv("nodes.csv", index=False)
  description.to_csv("description.csv", index=False)
  relationships.to_csv("relationship.csv", index=False)


def create_indexes(transaction):
  """
  Creates indices over the most used database properties
  """
  transaction.run("CREATE INDEX FOR (c:Concept) ON (c.id);")
  transaction.run("CREATE INDEX FOR (r:Relationship) ON (r.sourceId);")
  transaction.run("CREATE INDEX FOR (r:Relationship) ON (r.destinationId);")
  transaction.run("CREATE INDEX FOR (r:Relationship) ON (r.typeId);")


def populate_nodes(transaction, nodes, descriptions, batch_size=1000):
  """
  Populates the nodes and descriptions
  """

  # Populates the nodes first
  for i in range(0, len(nodes), batch_size):
        batch = nodes.iloc[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} of {len(nodes) // batch_size + 1} Concept nodes.")
        
        concept_query = """
        UNWIND $batch AS row
        CREATE (:Concept {
            id: row.id,  # Use the 'id' column for Concept nodes
            effectiveTime: row.effectiveTime, 
            moduleId: row.moduleId, 
            active: row.active, 
            definitionStatusId: row.definitionStatusId
        })
        """
        
        transaction.run(concept_query, batch=batch.to_dict('records'))
  
  # Next populates the descriptions that correspond with the nodes
  for i in range(0, len(descriptions), batch_size):
    batch = descriptions.iloc[i:i + batch_size]
    print(f"Processing batch {i // batch_size + 1} of {len(descriptions) // batch_size + 1} Descriptions.")
    
    # Create Description nodes and link them to Concept nodes in one step using UNWIND
    query = """
      UNWIND $batch AS row
      MERGE (d:Description {descriptionId: row.id})
      SET d.term = row.term, 
          d.languageCode = row.languageCode, 
          d.typeId = row.typeId, 
          d.caseSignificanceId = row.caseSignificanceId
      
      WITH d, row
      MERGE (c:Concept {id: row.conceptId})
      MERGE (c)-[:HAS_DESCRIPTION]->(d)
    """

    transaction.run(query, batch=batch.to_dict('records'))
    print(f"Batch {i // batch_size + 1}: Created and linked {len(batch)} Description nodes.")


def populate_relationships(transaction, relationships, batch_size=500):
    """
    Populates the relationships between nodes. There are four types of relationships that are seen in the relation_update() function.
    """

    # Go through relationship and create the relations between nodes
    for i in range(0, len(relationships), batch_size):
        batch = relationships.iloc[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1} of {len(relationships)//batch_size + 1} relationships")
        
        query = """
            UNWIND $batch AS row
            MATCH (source:Concept {id: row.sourceId}), (destination:Concept {id: row.destinationId})
            CREATE (source)-[:RELATIONSHIP {
                typeId: row.typeId,
                relationshipGroup: row.relationshipGroup,
                characteristicTypeId: row.characteristicTypeId,
                modifierId: row.modifierId
            }]->(destination)
            """

        transaction.run(query, batch=batch.to_dict('records'))


def relation_update():
  """
  The original relationship.csv contains numerical values so modified_relationship.csv contains the actual word for which each node corresponds to.
  """

  # Mapping the relationship number to the word
  relationship_group_mapping = {
    0: "ATTRIBUTE",
    1: 'IS_A',
    2: 'PART_OF',
    3: 'ASSOCIATED_WITH',
    4: 'CAUSES',
    5: 'FOUND_AT',
    6: "TEMPORAL"
  }

  # Not all the columns are needed
  columns_to_drop = [
      "id",
      "effectiveTime",
      "active",
      "moduleId",
      "relationshipGroup",
      "typeId",
      "characteristicTypeId",
      "modifierId"
  ]
  
  # Let pandas go over the CSV
  relationships_df = pd.read_csv('CSVItems/relationship.csv')

  # Maps and deletes columns
  relationships_df['relationshipType'] = relationships_df['relationshipGroup'].map(relationship_group_mapping)
  relationships_df.drop(columns=columns_to_drop, inplace=True)

  # Finally, convert the fixes to a new modified_relationship.csv file
  relationships_df.to_csv('modified_relationship.csv', index=False)


def fixDescription(description):
  """
  Description CSV has errors has the term column has commas within the term segment. Additionally, there are quotations which were removed manually. 
  """

  # nodes = pd.read_csv(node, sep='\t', dtype=str)
  # relationships = pd.read_csv(relationship, sep='\t', dtype=str)

  with open(description, 'r', encoding='utf-8') as file:
        content = file.read().replace(',', '')
        
  with open(description, 'w', encoding='utf-8') as file:
        file.write(content)

  description = pd.read_csv(description, sep='\t', dtype=str)
  description.to_csv("description.csv", index=False)


def clean_csv(input_path, output_path):
    """
    There is also encoding issues has the data wasn't in UTF-8 format so it was rewritten.
    """

    # Reopen and fix encoding issues
    with open(input_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            if len(row) == 0 or any(cell.strip() == "" for cell in row):
                continue
            writer.writerow(row)
        print("Clean-up complete.")


def combine_nodes():
  """
  We can combine certain elements of nodes.csv and description.csv to allow for faster uploading.
  """

  # We join the nodes.id with the descriptions.conceptId
  nodes = pd.read_csv("CSVItem/nodes.csv", usecols=["id", "active"], dtype={"id": "int"})
  descriptions = pd.read_csv("CSVItem/description.csv", usecols=["conceptId", "term", "effectiveTime"])

  # Drop all rows with NaN values
  descriptions = descriptions.dropna(subset=["conceptId"])
  descriptions["conceptId"] = descriptions["conceptId"].astype(int)  # convert to int

  # Fill all effectiveTime to 0 if they are null then convert to integer
  descriptions["effectiveTime"] = pd.to_numeric(descriptions["effectiveTime"], errors='coerce')
  descriptions["effectiveTime"] = descriptions["effectiveTime"].fillna(0).astype(int)

  # Merge the two
  merged = pd.merge(nodes, descriptions, left_on="id", right_on="conceptId", how="left")

  # This isn't needed, we'll delete it
  merged.drop(columns=["conceptId"], inplace=True)

  # There are multiple terms for each ID so we join them together with the semicolon
  merged = merged.groupby(["id", "active"])["term"].apply(lambda x: ';'.join(x.astype(str))).reset_index()
  merged = merged.rename(columns={"term": "descriptions"})

  # Convert to CSV
  merged.to_csv("CSVItem/merged_nodes.csv", index=False)


def main():
  uri = "bolt://localhost:7687"
  username = "neo4j"
  password = "MedicalRAG"

  # Get information
  node, descriptio, relationship = local_requirements()

  nodes = pd.read_csv(node)
  description = pd.read_csv(descriptio)
  relationships = pd.read_csv(relationship)

  # Make CSV
  to_csv(nodes, description, relationships)

  # Connect to Neo4J
  driver = GraphDatabase.driver(uri, auth=(username, password))

  # Fix relationships to get modified_relationship.csv
  relation_update()

  # Fix and clean descriptions
  fixDescription(descriptio)
  clean_csv(relationship, "CSVItems/modified_relationship.csv")

  # Combine description with the nodes
  combine_nodes()

  # Populate the database
  with driver.session() as session:
    session.execute_write(create_indexes)
    session.execute_write(populate_nodes, node=nodes, description=description)
    session.execute_write(populate_relationships, relationships)


if __name__ == "__main__":
  main()