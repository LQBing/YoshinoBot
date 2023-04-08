FROM python:3.9-slim
WORKDIR /workdir
# RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g;s/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list && \
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && pip config set install.trusted-host mirrors.aliyun.com
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD . .
ENTRYPOINT [ "python", "run.py"]
