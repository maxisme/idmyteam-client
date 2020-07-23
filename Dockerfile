FROM maxisme/rpi-opencv

RUN mkdir -p /usr/src/idmyteam

WORKDIR /usr/src/idmyteam
COPY . .

RUN pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/idmyteam/:/usr/src/idmyteam/web/:/usr/src/idmyteam/settings/"
RUN python web/client.py

ENTRYPOINT ["python", "web/client.py"]