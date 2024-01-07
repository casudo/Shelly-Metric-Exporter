FROM python:3.8-slim-buster 

### Set working directory and copy files
RUN mkdir /code
WORKDIR /code
ADD . /code/

### Make script executable
RUN chmod 770 /code/app.py

### Install dependencies
RUN pip install -r requirements.txt

### Set entrypoint
### https://stackoverflow.com/a/29745541
ENTRYPOINT ["python3", "-u", "/code/entrypoint.py"]