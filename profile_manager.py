import os
import json
import urllib.request
import urllib.error
from datetime import datetime

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "kelvinvelasquez-SDE"
# Resolve README path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(SCRIPT_DIR, "README.md")

def fetch_recent_activity():
    """Fetch recent PRs and issues using GitHub GraphQL API via urllib."""
    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN not set.")
        return []

    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Antigravity-Agent"
    }
    query = """
    {
      user(login: "%s") {
        pullRequests(first: 10, orderBy: {field: CREATED_AT, direction: DESC}, states: [OPEN, MERGED]) {
          nodes {
            title
            url
            state
            createdAt
            repository {
              nameWithOwner
              url
            }
          }
        }
      }
    }
    """ % USERNAME
    
    data = {"query": query}
    json_data = json.dumps(data).encode("utf-8")
    
    req = urllib.request.Request(url, data=json_data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("data", {}).get("user", {}).get("pullRequests", {}).get("nodes", [])
    except urllib.error.URLError as e:
        print(f"Error fetching data: {e}")
        return []

def format_activity_table(activity_nodes):
    lines = [
        "| Project | Description | Status | Date |",
        "| :--- | :--- | :---: | :---: |"
    ]
    
    for item in activity_nodes:
        repo_name = item['repository']['nameWithOwner']
        repo_url = item['repository']['url']
        desc = item['title']
        url = item['url']
        state = item['state']
        date_str = item['createdAt']
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").strftime("%b %d")
        
        status_icon = "🟣 Merged" if state == "MERGED" else "🟢 Open"
        if state == "CLOSED": status_icon = "🔴 Closed"
        
        # Truncate desc if too long
        if len(desc) > 60:
            desc = desc[:57] + "..."
            
        line = f"| [{repo_name}]({repo_url}) | [{desc}]({url}) | {status_icon} | {date} |"
        lines.append(line)
        
    return "\n".join(lines)

def generate_header():
    return f"""
<div align="center">
  <h1>Hi there, I'm Kelvin Velásquez! 👋</h1>
  <h3>Software Development Engineer | Open Source Enthusiast</h3>
  
  <p>
    Building robust, scalable, and "Ultra Pro" software solutions.
  </p>

  <a href="https://linkedin.com/in/kelvin-velasquez" target="_blank">
    <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
  </a>
  <a href="mailto:kelvinvelasquez080@gmail.com">
    <img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/>
  </a>
</div>

---
"""

def generate_stats_section():
    # Helper to generate the stats URLs
    # Using github-readme-stats and skill-icons
    return f"""
<div align="center">
  <h2>⚡ Tech Stack & Stats</h2>
  
  <br>
  
  <!-- Tech Stack -->
  <p align="center">
    <a href="https://skillicons.dev">
      <img src="https://skillicons.dev/icons?i=python,js,ts,react,nextjs,nodejs,linux,docker,git,github,vscode,vim&perline=12" />
    </a>
  </p>

  <br>

  <!-- GitHub Stats -->
  <p align="center">
    <img src="https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight&hide_border=true&bg_color=00000000" alt="Kelvin's Stats" height="180"/>
    <img src="https://github-readme-stats.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&theme=tokyonight&hide_border=true&bg_color=00000000" alt="Top Languages" height="180"/>
  </p>
  
  <!-- Streak -->
  <p align="center">
    <img src="https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=tokyonight&hide_border=true&background=00000000" alt="GitHub Streak" />
  </p>
</div>
"""

def update_readme():
    activity = fetch_recent_activity()
    activity_table = format_activity_table(activity)
    
    header = generate_header()
    stats = generate_stats_section()
    
    # Assembly
    content = f"{header}\n{stats}\n\n## 🚀 Recent Activity\n<!-- START_ACTIVITY -->\n{activity_table}\n<!-- END_ACTIVITY -->\n\n<div align='center'>\n  <sub>Automated by Antigravity 🚀</sub>\n</div>"
    
    # Ensure directory exists just in case (though it should be the repo root)
    if not os.path.exists(README_PATH) and "/" in README_PATH:
         os.makedirs(os.path.dirname(README_PATH), exist_ok=True)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("README.md updated successfully.")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("Warning: GITHUB_TOKEN not set, skipping API calls for local test if needed.")
    update_readme()
