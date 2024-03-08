FROM python:3.9

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY requirements.txt .

RUN pip install gunicorn

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["bash", "-c", "./scripts/wait-for-it.sh db:5432 -- ./manage.py migrate && gunicorn -b 0.0.0.0:8000 foodgram.wsgi"]
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
