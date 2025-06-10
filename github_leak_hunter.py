
```python
import requests
import argparse
import re
import os

GITHUB_API = "https://api.github.com/search/code"
HEADERS = {
    "Accept": "application/vnd.github+json",
}

def search_github(query, token):
    headers = HEADERS.copy()
    headers["Authorization"] = f"token {token}"
    params = {
        "q": query,
        "per_page": 100
    }

    try:
        response = requests.get(GITHUB_API, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"[!] Error during GitHub search: {e}")
        return []

def extract_info_from_items(items):
    results = []
    for item in items:
        repo = item['repository']['full_name']
        file_path = item['path']
        html_url = item['html_url']
        results.append((repo, file_path, html_url))
    return results

def main(query, token, regex=None):
    print(f"[+] Searching GitHub for leaks related to: {query}")
    items = search_github(query, token)
    leaks = extract_info_from_items(items)

    if not leaks:
        print("[-] No leaks found.")
        return

    print(f"[✓] Found {len(leaks)} possible leaks:")
    for repo, path, url in leaks:
        print(f" - {repo}/{path}: {url}")
        if regex:
            try:
                raw_url = url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                content = requests.get(raw_url).text
                matches = re.findall(regex, content)
                if matches:
                    print(f" └─ Secret match: {matches}")
            except:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find secrets in GitHub repos via search API.")
    parser.add_argument("query", help="Search query (e.g. site.com OR API name)")
    parser.add_argument("--token", help="GitHub Personal Access Token", required=True)
    parser.add_argument("--regex", help="Optional regex to match secrets in raw file", default=None)
    args = parser.parse_args()

    main(args.query, args.token, args.regex)
```
