from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

# Use CodeLlama:7B via Ollama
llm = OllamaLLM(model="codellama:7b")

# Define the prompt template
prompt = PromptTemplate(
    input_variables=["user_request"],
    template="Write Python code for the following request in a microservice format. Start with a brief comment explaining what the microservice does, then provide only executable Python code structured as a microservice with:\n\n- FastAPI or Flask framework\n- Proper API endpoints\n- Request/response models\n- Error handling\n- Main function to run the service\n\nRequest: {user_request}\n\nFormat your response as complete Python microservice code with comments at the beginning explaining the functionality."
)

# Combine prompt and LLM into a runnable chain
chain = prompt | llm

# Get user input
user_input = input("Describe the Python code you want: ")

# Run the chain and print the output
output = chain.invoke({"user_request": user_input})

print("\nGenerated Python Code:\n")
print(output)
