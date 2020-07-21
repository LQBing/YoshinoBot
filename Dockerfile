FROM python:3-slim-buster
WORKDIR /workdir
ADD . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "run.py"]
