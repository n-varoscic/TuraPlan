# Slika za backend: Python 3.12 z nameščenimi knjižnicami iz requirements.txt
FROM python:3.12-slim

# Python ne piše .pyc datotek in izpis takoj pošlje v dnevnik
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Najprej samo requirements.txt, da Docker knjižnic ne nameša ob vsaki spremembi kode
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 0.0.0.0 pomeni, da je strežnik dosegljiv tudi izven vsebnika
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
