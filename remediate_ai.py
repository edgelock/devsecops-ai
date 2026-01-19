import os, requests

# --- 1. SETUP: LOAD SECRETS ---
api_key = os.getenv("AZURE_OPENAI_KEY")
raw_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
gh_token = os.getenv("GITHUB_TOKEN")
repo, pr_number = os.getenv("GITHUB_REPOSITORY"), os.getenv("PR_NUMBER")

# YOUR SPECIFIC DEPLOYMENT NAME
DEPLOYMENT_NAME = "security-expert-model"

def get_ai_fix(issue):
    """Asks the AI to fix a specific security vulnerability."""
    # We clean the URL to ensure it doesn't have extra paths
    base_url = raw_endpoint.split("/openai")[0].rstrip("/")
    url = f"{base_url}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-15-preview"
    
    headers = {"Content-Type": "application/json", "api-key": api_key}
    data = {
        "messages": [
            {"role": "system", "content": "You are a DevSecOps expert. Provide only the secure Terraform HCL code to fix the issue provided."},
            {"role": "user", "content": f"Fix this: {issue}"}
        ]
    }
    
    print(f"DEBUG: Calling AI at {url}")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        print(f"!!! API ERROR: {response.status_code} - {response.text}")
        return None
        
    return response.json()['choices'][0]['message']['content']

def post_to_pr(suggestion):
    """Automatically posts the AI's fix as a comment on the Pull Request."""
    if not suggestion: return
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"}
    requests.post(url, headers=headers, json={"body": f"### 🛡️ AI Security Remediation\n\n{suggestion}"})

if pr_number:
    # Simulating finding a vulnerability in the lab
    flaw = "Storage account has 'public_network_access_enabled' set to true."
    post_to_pr(get_ai_fix(flaw))