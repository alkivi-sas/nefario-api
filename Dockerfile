FROM python:3.6-alpine3.6
ADD nefario /nefario
COPY requirements.txt /nefario
WORKDIR /nefario
RUN pip install -r requirements.txt
RUN apk update && apk add --no-cache git
RUN pip install git+https://github.com/saltstack/pepper.git
COPY start.sh /
RUN chmod +x /start.sh
ENTRYPOINT /start.sh
