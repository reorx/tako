# pull official base image
FROM python:3.12-alpine

# set working directory
WORKDIR /app

# install python dependencies
ADD requirements.txt .
RUN pip install -r requirements.txt

# add app
ADD *.py .
ADD tako ./tako

# collect static files
RUN python manage.py collectstatic

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_ROOT_USER_ACTION=ignore PYTHONPATH=.

CMD ["gunicorn"]
