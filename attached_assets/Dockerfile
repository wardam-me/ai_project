FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    dbus \
    dbus-x11 \
    python3 \
    python3-pip

RUN pip3 install bleak

COPY app.py /app.py

CMD ["python3", "/app.py"]
