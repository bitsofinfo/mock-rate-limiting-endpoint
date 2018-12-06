FROM python:3.6.5-alpine

# install the result handler and reactor module /usr/local/bin
RUN apk update ; \
    apk upgrade ; \
    apk add git build-base; \
    echo $PATH ; \
    git clone https://github.com/bitsofinfo/mock-rate-limiting-endpoint.git ; \
    cp /mock-rate-limiting-endpoint/*.py /usr/local/bin/ ; \
    rm -rf /mock-rate-limiting-endpoint ; \
    pip install --upgrade pip twisted ratelimit ; \
    easy_install --upgrade pytz ; \
    cd /tmp ; \
    apk del git build-base ; \
    ls -al /usr/local/bin ; \
    rm -rf /var/cache/apk/* ; \
    chmod +x /usr/local/bin/*.py
