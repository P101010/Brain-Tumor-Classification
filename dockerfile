FROM python:3.8
LABEL maintainer="Aadarsh"

ARG AIRFLOW_VERSION=2.0.2
ARG AIRFLOW_HOME=/mnt/airflow

WORKDIR ${AIRFLOW_HOME}
ENV AIRFLOW_HOME=${AIRFLOW_HOME}

RUN apt-get update -yqq && \
    apt-get install -yqq --no-install-recommends \
    wget \
    curl \
    git \
    gcc \
    libhdf5-dev \
    libleveldb-dev \
    && apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /requirements.txt

# Upgrade pip separately to catch any issues
RUN pip install --upgrade pip && \
    useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow && \
    pip install apache-airflow==${AIRFLOW_VERSION} && \
    pip install -r /requirements.txt

COPY ./entrypoint.sh ${AIRFLOW_HOME}/entrypoint.sh

# Ensure the entrypoint script is executable
RUN chmod +x ${AIRFLOW_HOME}/entrypoint.sh

# Copy the Airflow scripts
COPY ./src ${AIRFLOW_HOME}/

# Set ownership and permissions
RUN chown -R airflow: ${AIRFLOW_HOME}

USER airflow

ENV GOOGLE_APPLICATION_CREDENTIALS=/mnt/airflow/keys/tensile-topic-424308-d9-7418db5a1c90.json
EXPOSE 8080
EXPOSE 8888

ENTRYPOINT [ "/mnt/airflow/entrypoint.sh" ]
