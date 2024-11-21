# MedicalRAG - A Medical Disease & Treatment Chatbot

MedicalRAG is a medical chatbot powered by FastAPI, OpenAI's GPT model, and a knowledge graph (Neo4j). The chatbot helps users identify possible medical conditions and recommend treatments based on the symptoms they provide. It extracts symptoms from user input, queries a medical knowledge graph, and generates a response that suggests possible conditions and treatments.

## Features

- **Symptom Extraction**: Extracts specific symptoms from a user's input using GPT-3.5.
- **Disease Prediction**: Utilizes a Neo4j-powered medical knowledge graph to suggest possible conditions based on the input symptoms.
- **Treatment Recommendations**: Based on identified diseases, the bot suggests treatments or advice.
- **Multiple Conversations**: Users can start new conversations or continue existing ones.
- **FastAPI Backend**: The backend serves the chatbot responses, running on a local FastAPI server.
- **Real-Time Interaction**: The chatbot responds in real-time to user queries.

## Technologies Used

- **Streamlit**: For the front-end UI of the chatbot.
- **FastAPI**: To handle API calls for disease prediction and treatment recommendations.
- **OpenAI (GPT-3.5)**: For symptom extraction and generating responses.
- **Neo4j**: A graph database used for storing and querying medical knowledge.
- **Transformers (Hugging Face)**: For embedding generation using ClinicalBERT.
- **Python**: Backend language.


## Requirements

Before you can run the project, you'll need to install the required dependencies. You can use `pip` to install them.

### Prerequisites

- Python 3.8+
- Neo4j Database
- OpenAI API Key (for accessing GPT-3.5)
- SSL Configuration (if using a secure connection to Neo4j)

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/nimithejeagerist/neodatahackathon.git
    cd neodatahackathon
    ```

2. **Install dependencies**:
    Create a virtual environment and install the required dependencies:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Run the app**:

      ```bash
      streamlit run main.py
      ```

## How It Works

### Symptom Extraction
When the user enters a set of symptoms, the system uses OpenAI's GPT-3.5 model to extract specific, identifiable medical symptoms from the user's input. It ignores general terms and returns a comma-separated list of symptoms.

### Disease Prediction
Using the extracted symptoms, the system queries a Neo4j-powered knowledge graph for possible diseases. Each disease is associated with specific symptoms and relationships in the knowledge graph. The system returns the most relevant diseases based on the similarity between the symptoms and the nodes in the graph.

### Treatment Recommendations
For each identified disease, the system provides recommended actions or treatments. The recommendations are based on predefined information stored in the `context` and potentially other data in the knowledge graph.

## Project Structure

```
MedicalRAG/
│
├── graphConstruction         # Contained the data and the preprocessing file
│   └── medical_rag.py        # Preprocesses data
├── api.py                    # FastAPI server and endpoints
├── main.py                   # Streamlit UI
├── retriever.py              # RAG implementation  
├── .env                      # Environment variables (OpenAI API key, Neo4j credentials)
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Images of the Knowledge Graph
![Screenshot 2024-11-16 095844](https://github.com/user-attachments/assets/f6b20a99-7dec-4c4c-bc55-70e1ae84cf45)
![Screenshot 2024-11-17 202538](https://github.com/user-attachments/assets/86b3da7d-ad12-413c-8ed6-368cffbbd72f)
![Screenshot 2024-11-17 202526](https://github.com/user-attachments/assets/4c5292cb-19ff-406a-8ec7-9bb4ed97f3e4)
![Screenshot 2024-11-16 100159](https://github.com/user-attachments/assets/ffd5d9ac-0a71-4782-8bf1-f16140701f2d)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##Citations
ClincalBERT: Wang, G., Liu, X., Ying, Z. et al. Optimized glycemic control of type 2 diabetes with reinforcement learning: a proof-of-concept trial. Nat Med (2023). https://doi.org/10.1038/s41591-023-02552-9
