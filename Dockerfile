FROM python:3.8

RUN python -m pip install --upgrade pip
RUN pip install pipenv

WORKDIR /code

COPY ./Pipfile  .

RUN pipenv install --deploy --ignore-pipfile

# Copy project
COPY . . 

RUN chmod +x run.sh
RUN ./run.sh