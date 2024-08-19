FROM python:3.10-slim

# Update pip as certain packages (ex: XGBoost) need certain versions of pip
RUN pip install -U pip
RUN pip install pipenv

#Creates and cd's into the /app directory
WORKDIR /app
COPY ["Pipfile", "Pipfile.lock", "./"]
#--system installs the environment in the parent OS in the container
#--deploy makes sure Pipfile.lock is up-to-date and will crash if it isn't
RUN pipenv install --system --deploy


COPY ["model.py", "predict.py",  "./" ]

EXPOSE 9696

ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:9696", "predict:app" ]
