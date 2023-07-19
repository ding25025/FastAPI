# CompalAPI
## Swagger API Document
http://127.0.0.1:8000/docs/

# start 
http://127.0.0.1:8000
- python3 main.py

## create requirements.txt
- pip3 freeze > requirements.txt

## build docker image

```
docker image build -t compalapi_test .

```
 
## run docker image

```
docker run --restart=always -p 8000:8000  --network=host -t compalapi_test

```