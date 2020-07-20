FROM python:3
WORKDIR /workdir
# ADD requirements.txt .
# ADD run.py .
# ADD hoshino .
ADD . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "run.py"]
# ENTRYPOINT [ "bash" ]

