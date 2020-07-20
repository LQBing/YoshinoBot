FROM python:3
WORKDIR /workdir
ADD . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "run.py"]
