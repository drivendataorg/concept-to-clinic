FROM ubuntu:rolling
ENV PYTHONUNBUFFERED 1
RUN apt-get update && apt-get install -y tcl tk python3.6 python3.6-tk wget python-opencv
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py

# Default to Python 3.6
RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3.6 /usr/bin/python

# Prediction
COPY prediction/.pylidcrc /root/.pylidcrc
COPY ./prediction/requirements/torch.txt /requirements/prediction/torch.txt
RUN pip install -r /requirements/prediction/torch.txt
COPY ./prediction/requirements/local.txt /requirements/prediction/local.txt
RUN pip install -r /requirements/prediction/local.txt
COPY ./prediction/requirements/base.txt /requirements/prediction/base.txt
RUN pip install -r /requirements/prediction/base.txt

RUN pip install gunicorn
RUN pip install gevent

COPY ./prediction /app
COPY ./compose/prediction/gunicorn.sh /app/gunicorn.sh

WORKDIR /app

RUN chmod +x gunicorn.sh

ENTRYPOINT ["/app/gunicorn.sh"]
