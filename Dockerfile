FROM python:3.9.15
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN apt update --quiet && apt install libgl1-mesa-glx -y --quiet
COPY . .
CMD [ "python3", "server.py" ]
