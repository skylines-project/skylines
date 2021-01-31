# Use Python 2.7 by default, but allow
# e.g. `--build-arg PYTHON_VERSION=3.6` usage
ARG PYTHON_VERSION=2.7
FROM python:${PYTHON_VERSION}

RUN pip install --upgrade pip
RUN pip install --upgrade virtualenv
RUN pip install pipenv==v2020.11.15

WORKDIR /home/skylines/code/

# Install Python dependencies
COPY Pipfile Pipfile.lock /home/skylines/code/
RUN pipenv install --dev --python=${PYTHON_VERSION}

# Run the development server by default
CMD ["pipenv", "run", "./manage.py", "runserver"]
