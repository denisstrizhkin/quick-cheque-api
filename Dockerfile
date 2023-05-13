FROM python:3.11-bullseye

WORKDIR /var/app

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV FLASK_ENV=development

USER nobody

CMD ["flask", "run", "-h", "0.0.0.0"]
