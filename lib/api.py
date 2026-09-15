import requests


def fetch_data():
    """Fetch the sample post, returning an empty dictionary on failure."""
    try:
        response = requests.get(
            "https://jsonplaceholder.typicode.com/posts/1", timeout=10
        )
        if response.status_code == 200:
            post = response.json()
            if isinstance(post, dict):
                return post
    except (requests.RequestException, ValueError):
        pass
    return {}
