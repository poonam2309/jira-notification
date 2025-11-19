#!/usr/bin/env python3
import os
import json
import requests
import base64
import textwrap
import sys


def require_env(name):
    value = os.getenv(name)
    if not value:
        print(f"ERROR: Missing environment variable: {name}", file=sys.stderr)
        sys.exit(1)
    return value


# --------------------
# MAIN SCRIPT
# --------------------
jira_base = require_env("JIRA_BASE_URL").rstrip("/")
jira_email = require_env("JIRA_EMAIL")
jira_api_token = require_env("JIRA_API_TOKEN")
jira_project = require_env("JIRA_PROJECT_KEY")

# GitHub context for description
repo = os.getenv("GITHUB_REPOSITORY", "unknown")
workflow = os.getenv("GITHUB_WORKFLOW", "workflow_dispatch")
actor = os.getenv("GITHUB_ACTOR", "unknown")
run_id = os.getenv("GITHUB_RUN_ID", "unknown")
server_url = os.getenv("GITHUB_SERVER_URL", "https://github.com")
run_url = f"{server_url}/{repo}/actions/runs/{run_id}"

summary = f"Story created from GitHub workflow_dispatch in {repo}"

description = textwrap.dedent(f"""
    A Story was automatically created due to a GitHub `workflow_dispatch` event.

    **Repository:** {repo}  
    **Workflow:** {workflow}  
    **Triggered by:** {actor}  
    **Run URL:** {run_url}  
""").strip()

payload = {
    "fields": {
        "project": {"key": jira_project},
        "summary": summary,
        "description": description,
        "issuetype": {"name": "Story"}      # <--- STORY TYPE
    }
}

# Auth header
encoded_auth = base64.b64encode(f"{jira_email}:{jira_api_token}".encode()).decode()

headers = {
    "Authorization": f"Basic {encoded_auth}",
    "Content-Type": "application/json"
}

url = f"{jira_base}/rest/api/3/issue"

print("Creating Jira Story...")
response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code not in [200, 201]:
    print(f"ERROR creating Jira Story: {response.status_code}")
    print(response.text)
    sys.exit(1)

data = response.json()
print(f"Successfully created Story: {data.get('key')}")
