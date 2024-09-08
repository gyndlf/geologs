![https://pypi.org/project/geologs](https://img.shields.io/pypi/v/geologs.svg) ![https://pypi.org/project/geologs](https://img.shields.io/pypi/wheel/geologs) ![](https://img.shields.io/badge/certified-cool_project-blue)


# Geologs - Slack Bot

- Runs basic system commands and pipes the output to slack
- Watches specified log files and parses new lines before posting them in a specific slack channel

Pull requests welcome.


## Installation
``
pip install geologs
``

A new Slack application needs to be made for each server. Use `manifest.json` as a template for the required permissions.

It is expected the API keys are given as environmental variables as `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`.

```
python -m geologs --conf=config.toml
```


## Configuration
Define the log files to listen to, delay in seconds between checking the file and an optional parser. 

Available parsers can be found in `geologs/parsers.py` to format the logs in a pretty format.

```toml
[testing]
channel = "#tephrite"
logfile = "test.log"
delay = 10
parser = "basic"

[test2]
channel = "#rocks-are-cool"
logfile = "test.log"
delay = 5
parser = "basic"
```

