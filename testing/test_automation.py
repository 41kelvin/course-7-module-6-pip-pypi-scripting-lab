import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest
import requests

from lib.api import fetch_data
from lib.generate_log import generate_log
from lib.tasks import UserAccount, load_accounts


def test_log_preserves_text_and_prints_filename(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    filename = generate_log(["  Keep spaces  ", "Café", ""])
    assert Path(filename).read_text(encoding="utf-8") == "  Keep spaces  \nCafé\n\n"
    assert capsys.readouterr().out == f"Log written to {filename}\n"


@pytest.mark.parametrize("data", [None, 1, {}, (), "entry"])
def test_invalid_log_input_does_not_create_files(data, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError):
        generate_log(data)
    assert list(tmp_path.iterdir()) == []


def test_fetch_data(monkeypatch):
    get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={"title": "Sample"})))
    monkeypatch.setattr("lib.api.requests.get", get)
    assert fetch_data() == {"title": "Sample"}
    assert get.call_args.kwargs["timeout"] == 10


@pytest.mark.parametrize("response", [
    Mock(status_code=503),
    Mock(status_code=200, json=Mock(side_effect=ValueError("Invalid JSON"))),
    Mock(status_code=200, json=Mock(return_value=[])),
])
def test_fetch_data_bad_response(response, monkeypatch):
    monkeypatch.setattr("lib.api.requests.get", Mock(return_value=response))
    assert fetch_data() == {}


def test_fetch_data_timeout(monkeypatch):
    monkeypatch.setattr("lib.api.requests.get", Mock(side_effect=requests.Timeout))
    assert fetch_data() == {}


def run_script(script, args, directory):
    root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        [sys.executable, str(root / script), *args], cwd=directory,
        text=True, capture_output=True, timeout=5,
    )


def test_log_script(tmp_path):
    result = run_script("generate_log.py", ["First entry", "Second entry"], tmp_path)
    assert result.returncode == 0, result.stderr
    logs = list(tmp_path.glob("log_*.txt"))
    assert len(logs) == 1
    assert logs[0].read_text() == "First entry\nSecond entry\n"


def test_task_commands_persist_and_separate_users(tmp_path):
    for username in ("kelvin", "sam"):
        result = run_script("main.py", ["add-task", "--user", username, "--title", "Study"], tmp_path)
        assert result.returncode == 0, result.stderr
        assert "Task added successfully!" in result.stdout
    result = run_script("main.py", ["complete-task", "--user", "kelvin", "--task-id", "1"], tmp_path)
    assert result.returncode == 0, result.stderr
    assert "Task marked as complete!" in result.stdout
    accounts = json.loads((tmp_path / "tasks.json").read_text())
    assert accounts["kelvin"][0]["completed"] is True
    assert accounts["sam"][0]["completed"] is False


def test_invalid_task_command_keeps_saved_data(tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text('{}\n')
    result = run_script("main.py", ["complete-task", "--user", "kelvin", "--task-id", "1"], tmp_path)
    assert result.returncode == 1
    assert "was not found" in result.stderr
    assert path.read_text() == '{}\n'


def test_account_validation_and_task_ids():
    with pytest.raises(ValueError):
        UserAccount(" ")
    account = UserAccount("kelvin")
    with pytest.raises(ValueError):
        account.add_task(" ")
    assert account.add_task("Study")["id"] == 1
    assert account.add_task("Practice")["id"] == 2
    account.complete_task(1)
    with pytest.raises(ValueError, match="already complete"):
        account.complete_task(1)
    assert account.tasks[1]["completed"] is False


@pytest.mark.parametrize("contents", ['{', '[]', '{"kelvin": [1]}'])
def test_invalid_saved_data(contents, tmp_path):
    path = tmp_path / "tasks.json"
    path.write_text(contents)
    with pytest.raises(ValueError):
        load_accounts(path)
    assert path.read_text() == contents
