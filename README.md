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
    git clone https://github.com/your-username/MedicalRAG.git
    cd MedicalRAG
    ```

2. **Install dependencies**:
    Create a virtual environment and install the required dependencies:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Set up the .env file**:
    Create a `.env` file in the root directory and add your environment variables:
    ```plaintext
    OPENAI_API_KEY=your-openai-api-key
    NEO4J_URI=neo4j://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=your-neo4j-password
    ```

4. **Install Neo4j**:
    - Make sure you have Neo4j running locally or connect to an existing instance.
    - For more details on installation, visit the [Neo4j documentation](https://neo4j.com/docs/).

5. **Run the app**:
    - Start the FastAPI server:
      ```bash
      uvicorn api:app --reload
      ```
    - Run the Streamlit front-end:
      ```bash
      streamlit run app.py
      ```

6. **Access the chatbot**:
    - Open your browser and navigate to [http://localhost:8501](http://localhost:8501) to interact with the chatbot.

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
├── api/                      # FastAPI backend
│   └── app.py                # FastAPI server and endpoints
│
├── app.py                    # Streamlit UI
├── .env                      # Environment variables (OpenAI API key, Neo4j credentials)
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Contributions

Feel free to contribute to this project! To contribute, fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

encoder:  Wang, G., Liu, X., Ying, Z. et al. Optimized glycemic control of type 2 diabetes with reinforcement learning: a proof-of-concept trial. Nat Med (2023). https://doi.org/10.1038/s41591-023-02552-9
