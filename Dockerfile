FROM python:3.6-alpine3.6
ADD nefario /nefario
COPY requirements.txt /nefario
WORKDIR /nefario
RUN pip install -r requirements.txt
CMD ["python", "app.py"]

