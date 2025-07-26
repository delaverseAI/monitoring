FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_DEBUG=False
ENV PORT=5000
ENV HOST=127.0.0.1

EXPOSE 5000

CMD [ "python3", "server.py"]