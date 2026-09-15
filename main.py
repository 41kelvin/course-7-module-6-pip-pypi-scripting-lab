import argparse

from lib.tasks import UserAccount, load_accounts, save_accounts


def main():
    parser = argparse.ArgumentParser(description="Manage tasks for user accounts.")
    parser.add_argument("--data-file", default="tasks.json", help="Task storage file")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add-task", help="Add a task to a user account")
    add.add_argument("--user", required=True)
    add.add_argument("--title", required=True)

    complete = commands.add_parser("complete-task", help="Mark a task as complete")
    complete.add_argument("--user", required=True)
    complete.add_argument("--task-id", required=True, type=int)
    args = parser.parse_args()

    try:
        accounts = load_accounts(args.data_file)
        username = args.user.strip()
        account = UserAccount(username, accounts.get(username))
        if args.command == "add-task":
            task = account.add_task(args.title)
            message = "Task added successfully!"
        else:
            task = account.complete_task(args.task_id)
            message = "Task marked as complete!"
        accounts[account.username] = account.tasks
        save_accounts(args.data_file, accounts)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")

    print(f"{message} {account.username}: {task['id']}. {task['title']}")


if __name__ == "__main__":
    main()
