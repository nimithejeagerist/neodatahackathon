from openai import OpenAI

client = OpenAI()

context = (
    "Possible diseases and treatments based on the symptoms provided:\n"
    "1. COVID-19: The recommended treatment is to see a doctor for proper testing and guidance.\n"
    "2. Common Cold: The recommended treatment is to drink warm fluids to help alleviate symptoms.\n"
)

prompt = (
    f"{context}\n"
    "Using only the information above, craft a message for the user. "
    "Do not add any extra information or make any assumptions. "
    "Follow this format:\n"
    "Possible Conditions: [List the conditions]\n"
    "Recommended Actions: [List the actions based on the treatments provided]\n"
    "Final Advice: [Encourage consulting a doctor if symptoms persist]"
    
)

# Make the API call
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}]
)

message = response.choices[0].message.content