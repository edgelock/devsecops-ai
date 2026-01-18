import os
import requests
import json

api_key = os.getenv("AZURE_OPENAI_KEY")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
gh_token = os.getenv("GITHUB_TOKEN")
repo = os.getenv("GITHUB_REPOSITORY")
pr_number = os.getenv("PR_NUMBER")

def get_ai_fix(issue):
    headers = {"Content-Type": "application/json", "api-key": api_key}
    data = {
        "messages": [
            {"role": "system", "content": "You are a DevSecOps Lead. Provide the specific Terraform HCL code to fix the vulnerability."},
            {"role": "user", "content": f"Fix this: {issue}"}
        ],
        "max_tokens": 300
    }
    
    response = requests.post(f"{endpoint}/openai/deployments/security-fixer/chat/completions?api-version=2024-02-15-preview", headers=headers, json=data)
    
    # --- ERROR HANDLING START ---
    result = response.json()
    if "error" in result:
        print(f"!!! API ERROR: {result['error']['message']}")
        return None
    # --- ERROR HANDLING END ---
    
    return result['choices'][0]['message']['content']

def post_to_pr(suggestion):
    if not suggestion: return
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"token {gh_token}", "Accept": "application/vnd.github.v3+json"}
    requests.post(url, headers=headers, json={"body": f"### 🛡️ AI Security Remediation\n\n{suggestion}"})

if pr_number:
    fix = get_ai_fix("Storage account has public_network_access_enabled = true.")
    post_to_pr(fix)