FROM python:2.7-alpine

RUN apk update && \
    apk add tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" >  /etc/timezone && \
    apk del tzdata && \
    rm -r /var/cache/apk

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app

CMD ["python", "-m", "tgcnbot"]
