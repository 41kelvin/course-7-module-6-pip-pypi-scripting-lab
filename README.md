# Python Automation Lab

Generate daily text logs, fetch a sample API post, and manage tasks from the
command line. The task commands use a `UserAccount` class and save each user's
tasks in a JSON file.

## Setup

Use Python 3.10 or newer. From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate`.

`requirements.txt` was generated with `python -m pip freeze` in an isolated
virtual environment. It pins requests, pytest, and their installed dependencies.
The pip commands above are the setup used for this project.

## Generate a log

```bash
python generate_log.py
python generate_log.py "User logged in" "Report exported"
python generate_log.py --fetch-post
```

The default command writes three sample entries. Custom entries replace those
samples. `--fetch-post` fetches a title from JSONPlaceholder using requests and
includes it in the log. This option requires an internet connection and reports
an error if the request fails.

Each run writes `log_YYYYMMDD.txt` in the current working directory, using the
local date, and prints `Log written to log_YYYYMMDD.txt`. Running it again on the
same date overwrites that day's log.

The function can also be imported:

```python
from lib.generate_log import generate_log

filename = generate_log(["User logged in", "Report exported"])
```

`generate_log(data)` requires a list, writes one entry per line, and returns the
filename. An empty list creates an empty file. Non-list input raises `ValueError`.
Text entries retain their whitespace and Unicode characters.

## Manage tasks

```bash
python main.py add-task --user kelvin --title "Finish the lab"
python main.py complete-task --user kelvin --task-id 1
```

The add command prints the new task ID. Task IDs start at 1 for each account.
Tasks are stored in `tasks.json` in the current directory and survive separate
script runs. Empty usernames and titles, missing task IDs, and already completed
tasks produce an error message and a nonzero exit code.

To choose a different storage file, put `--data-file` before the command:

```bash
python main.py --data-file study.json add-task --user kelvin --title "Review notes"
```

Run `python main.py --help` or `python generate_log.py --help` for command help.
The task file is intended for one local process at a time.

## Project files

- `lib/generate_log.py`: log generation and input validation.
- `lib/api.py`: public API request with a ten-second timeout.
- `lib/tasks.py`: user accounts and JSON storage.
- `generate_log.py`: log script arguments.
- `main.py`: task command arguments.
- `testing/`: original lab tests and additional automation tests.

Generated logs, the default task file, caches, and the virtual environment are
excluded from Git.

## Tests

```bash
python -m pytest
```

The tests cover log naming, exact contents, invalid input, empty files,
confirmation messages, API responses and failures, task persistence, account
separation, and invalid task data. API tests use mock responses and need no
internet access. GitHub Actions runs the suite on Python 3.10 and 3.12.
