from python:3.7-slim

COPY *.py /
COPY requirements.txt /
RUN pip install --no-cache -r requirements.txt && \
  rm requirements.txt

CMD python /rpict3t1-to-mqtt.py
