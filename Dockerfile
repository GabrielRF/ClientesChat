FROM python:3.8-alpine

RUN pip install pytelegrambotapi
RUN pip install pymongo

add msgs.py /
add bot.py /

CMD [ "python", "./bot.py" ]
