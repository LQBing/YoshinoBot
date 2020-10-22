FROM python:3.8.6-slim-buster
WORKDIR /workdir
ADD . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "run.py"]
