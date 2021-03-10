FROM python:3

WORKDIR /tmp
COPY . /tmp

RUN pip install -r /tmp/requirements.txt

EXPOSE 5000

CMD ["python", "/tmp/main.py"]


USER root






