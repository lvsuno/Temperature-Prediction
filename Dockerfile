FROM mageai/mageai:0.9.71

ARG PROJECT_NAME=temperature_prediction
ARG MAGE_CODE_PATH=/home/src
ARG USER_CODE_PATH=${MAGE_CODE_PATH}/${PROJECT_NAME}

WORKDIR ${MAGE_CODE_PATH}

COPY ${PROJECT_NAME} ${PROJECT_NAME}



# Copy the data directory
COPY data  data

# COPY download_stations_id.py  download_stations_id.py


ENV USER_CODE_PATH=${USER_CODE_PATH}

# Update pip as certain packages (ex: XGBoost) need certain versions of pip
RUN pip install -U pip 
RUN pip install pipenv

# Install custom Python libraries and dependencies for your project.
RUN pip3 install -r ${USER_CODE_PATH}/requirements.txt

COPY ["Pipfile", "Pipfile.lock", "./"]
#--system installs the environment in the parent OS in the container
#--deploy makes sure Pipfile.lock is up-to-date and will crash if it isn't
RUN pipenv install --system --deploy

ENV PYTHONPATH="${PYTHONPATH}:${MAGE_CODE_PATH}/${PROJECT_NAME}"

# Installing necessary utilities and Terraform.
# Uncomment the following lines if you want to use Terraform in Docker.
RUN apt-get update && \
   apt-get install -y wget unzip && \
   wget https://releases.hashicorp.com/terraform/1.8.3/terraform_1.8.3_linux_amd64.zip && \
   unzip terraform_1.8.3_linux_amd64.zip -d /usr/local/bin/ && \
   rm terraform_1.8.3_linux_amd64.zip


RUN ls

CMD ["/bin/sh", "-c", "/app/run_app.sh"]

