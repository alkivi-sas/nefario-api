FROM python:alpine3.6
RUN apk update && apk add --no-cache git
ADD nefario /nefario
COPY requirements.txt /nefario
WORKDIR /nefario
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir git+https://github.com/saltstack/pepper.git
COPY start.sh /
RUN chmod +x /start.sh
ENTRYPOINT /start.sh
