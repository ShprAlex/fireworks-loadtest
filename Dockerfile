FROM python:3.12-slim

WORKDIR /app

RUN pip install pipenv

# Copy the Pipfile and Pipfile.lock into the container
COPY Pipfile Pipfile.lock /app/

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the application code into the container
COPY . /app

ENTRYPOINT ["pipenv", "run", "python", "-u", "load_tester.py"]
