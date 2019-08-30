FROM node:12-alpine

RUN apk update && \
    apk add tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" >  /etc/timezone && \
    apk del tzdata && \
    rm -r /var/cache/apk

WORKDIR /app
COPY package*.json /app/
RUN npm install --production
COPY . /app
CMD ["npm", "run", "start"]
