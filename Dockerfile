FROM python:3.11-bullseye

WORKDIR /var/app

COPY requirements.txt .
RUN pip install -r requirements.txt

USER nobody

ENV FLASK_ENV=development
ENV FLASK_DEBUG=True

CMD ["flask", "run", "-h", "0.0.0.0"]
