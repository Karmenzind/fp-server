FROM karmenzind/fp-server:base
WORKDIR /fp_server
ADD ./src/ /fp_server
CMD redis-server /etc/redis.conf && python3 main.py
