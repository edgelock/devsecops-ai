import os
import requests

# --- 1. SET UP CREDENTIALS ---
# We fetch these from GitHub's secret storage
api_key = os.getenv("AZURE_OPENAI_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
gh_token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

def get_ai_fix(issue_description):
    """Sends a security error to Azure AI and asks for the corrected code."""
    headers = {"Content-Type": "application/json", "api-key": api_key}
    
    # We tell the AI how to behave (The System Prompt)
    data = {
        "messages": [
            {"role": "system", "content": "You are a DevSecOps Lead. Provide the specific Terraform HCL code line to fix the reported security vulnerability."},
            {"role": "user", "content": f"How do I fix this Terraform vulnerability: {issue_description}"}
        ],
        "max_tokens": 300
    }

    # Request the fix from your Azure model
    response = requests.post(f"{endpoint}/openai/deployments/security-fixer/chat/completions?api-version=2024-02-15-preview", 
                             headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

def post_comment_to_pr(ai_message):
    """Automatically posts the AI's advice to your GitHub Pull Request."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"}
    requests.post(url, headers=headers, json={"body": f"### 🛡️ AI Security Remediation\n\n{ai_message}"})

# --- 2. EXECUTE ---
if pr_number:
    # We are simulating a scan result here for the lab
    security_flaw = "Storage account 'insecure' has 'public_network_access_enabled' set to true."
    fix_suggestion = get_ai_fix(security_flaw)
    post_comment_to_pr(fix_suggestion)