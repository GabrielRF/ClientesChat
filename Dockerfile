FROM python:3.8-alpine

RUN pip install pytelegrambotapi
RUN pip install pymongo
RUN pip install pymongo[tls]
RUN pip install pymongo[srv]

add msgs.py /
add bot.py /

CMD [ "python", "./bot.py" ]
