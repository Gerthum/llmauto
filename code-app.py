from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
from functions import create_quick_pr, configure_target_repo

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # This loads .env file automatically
    print("Environment variables loaded from .env file")
except ImportError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("Environment variables will only be loaded from system environment.")

# Optional: Allow user to override target repository
import os
current_repo = os.getenv('GITHUB_REPO', 'Gerthum/task-tracker')
print(f"Target repository: {current_repo}")
change_repo = input(f"Change target repository? (current: {current_repo}) [y/N]: ").lower().strip()
if change_repo in ['y', 'yes']:
    new_repo = input("Enter repository (owner/repo): ").strip()
    new_branch = input("Enter default branch [main]: ").strip() or "main"
    configure_target_repo(new_repo, new_branch)

# Use CodeLlama:7B via Ollama
llm = OllamaLLM(model="codellama:7b")

# Define the prompt template for code generation
prompt = PromptTemplate(
    input_variables=["user_request"],
    template="Write Python code for the following request in a microservice format. Start with a brief comment explaining what the microservice does, then provide only executable Python code structured as a microservice with:\n\n- FastAPI or Flask framework\n- Proper API endpoints\n- Request/response models\n- Error handling\n- Main function to run the service\n\nRequest: {user_request}\n\nFormat your response as complete Python microservice code with comments at the beginning explaining the functionality."
)

# Define the prompt template for filename suggestion
filename_prompt = PromptTemplate(
    input_variables=["user_request"],
    template="Based on this request: '{user_request}', suggest a good Python filename for a microservice. Respond with only the filename ending in .py, nothing else. Example format: user_service.py"
)

# Combine prompts and LLM into runnable chains
code_chain = prompt | llm
filename_chain = filename_prompt | llm

# Get user input
user_input = input("Describe the Python code you want: ")

# Get suggested filename from LLM
print("\nGenerating filename suggestion...")
suggested_filename = filename_chain.invoke({"user_request": user_input}).strip()

# Clean up the suggested filename (remove any extra text)
if suggested_filename.endswith('.py'):
    suggested_filename = suggested_filename
else:
    suggested_filename = suggested_filename + '.py'

# Ask user for filename with suggestion
filename_input = input(f"Enter filename (press Enter to use '{suggested_filename}'): ").strip()
filename = filename_input if filename_input else suggested_filename

print(f"Using filename: {filename}")

# Run the chain and print the output
output = code_chain.invoke({"user_request": user_input})

print("\nGenerated Python Code:\n")
print(output)

# Ask if user wants to create a PR
create_pr = input("\nDo you want to create a GitHub PR with this code? (y/n): ").lower().strip()

if create_pr in ['y', 'yes']:
    try:
        # Create description for the PR
        pr_description = f"Auto-generated microservice code for: {user_input}\n\nGenerated using CodeLlama via Ollama."
        
        # Create the PR
        print("\nCreating GitHub Pull Request...")
        pr_url = create_quick_pr(
            code=output,
            filename=filename,
            description=pr_description
        )
        
        print(f"Pull Request created successfully!")
        print(f"PR URL: {pr_url}")
        
    except Exception as e:
        print(f"Failed to create PR: {str(e)}")
        print("Make sure your .env file has GITHUB_TOKEN and GITHUB_REPO set correctly")
else:
    print("Code generated successfully. No PR created.")