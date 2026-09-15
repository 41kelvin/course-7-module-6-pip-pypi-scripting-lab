import argparse

from lib.generate_log import generate_log


def main():
    parser = argparse.ArgumentParser(description="Write a dated text log.")
    parser.add_argument("entries", nargs="*", help="Log entries, quoted if they contain spaces")
    parser.add_argument("--fetch-post", action="store_true", help="Include a public API post title")
    args = parser.parse_args()

    entries = args.entries or [
        "User logged in", "User updated profile", "Report exported"
    ]
    if args.fetch_post:
        from lib.api import fetch_data

        post = fetch_data()
        if not post:
            parser.exit(1, "Could not fetch the post. Check your connection and try again.\n")
        title = post.get("title", "No title found")
        print(f"Fetched Post Title: {title}")
        entries.append(f"Fetched Post Title: {title}")

    try:
        generate_log(entries)
    except OSError as error:
        parser.exit(1, f"Could not write the log: {error}\n")


if __name__ == "__main__":
    main()
