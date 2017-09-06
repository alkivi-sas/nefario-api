FROM python:3.6-stretch
RUN apt-get update && apt-get install -y --no-install-recommends git gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
RUN pip install --no-cache-dir git+https://github.com/saltstack/pepper.git
ADD nefario /nefario
COPY config.py /
COPY manage.py /
COPY start.sh /
RUN chmod +x /start.sh
WORKDIR /
ENTRYPOINT /start.sh
