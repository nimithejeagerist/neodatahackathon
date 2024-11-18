import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

context = (
    "Possible diseases and treatments based on the symptoms provided:\n"
    "1. COVID-19: The recommended treatment is to see a doctor for proper testing and guidance.\n"
    "2. Common Cold: The recommended treatment is to drink warm fluids to help alleviate symptoms.\n"
)

def generate_response(answers):
    diseases_str = ", ". join(diseases)
    treatments_str = "\n".join([f"{d}: {', '.join(treatments[d])}" for d in treatments])   

    prompt = (
        f"{context}\n"
        "Using only the information above, craft a message for the user. "
        "Do not add any extra information or make any assumptions. "
        "Follow this format:\n"
        "Possible Conditions: {diseases_str}\n"
        "Recommended Actions: {treatments_str}\n"
        "Final Advice: [Encourage consulting a doctor if symptoms persist]"
    
    )

    # Make the API call
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()