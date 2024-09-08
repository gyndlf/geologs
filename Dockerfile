FROM python:3.12-slim

ADD config.toml .
RUN pip install geologs

CMD ["python", "-m",  "geologs", "--conf=config.toml"]
