FROM python

WORKDIR /app

COPY . /app

# RUN apt-get update

# RUN apt-get install nano

RUN pip3 install -r requirements.txt

CMD python3 main.py 