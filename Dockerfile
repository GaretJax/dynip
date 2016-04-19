FROM alpine:latest

RUN apk -U add python3
RUN pip3 install --upgrade pip
ADD requirements.txt /app/requirements.txt
RUN pip3 install --no-deps -r /app/requirements.txt

ADD . /app
WORKDIR /app
ENTRYPOINT ["python3", "dynip.py"]
