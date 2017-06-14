FROM python:3.6-alpine

WORKDIR /usr/src/app

RUN apk add --no-cache g++ gcc libxslt-dev

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY ./permit_finder /usr/src/app

CMD [ "python", "/usr/src/app/main.py"]