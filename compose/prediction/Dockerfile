FROM python:3.6
ENV PYTHONUNBUFFERED 1

RUN groupadd -r flask \
    && useradd -r -g flask flask

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./prediction/requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/prediction/gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod +x /gunicorn.sh

COPY . /app

RUN chown -R flask /app

USER flask

WORKDIR /app
