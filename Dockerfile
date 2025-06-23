FROM apache/beam_python3.11_sdk

# Install necessary packages.  Update first.
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk \
    default-jre \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME (important for JDBC drivers)
# ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"

# # Create a directory for the JDBC driver
# RUN mkdir -p /opt/jdbc

# # Copy the JDBC driver to the container
# COPY mssql-jdbc-12.8.1.jre11.jar /opt/jdbc/

COPY --from=apache/beam_python3.11_sdk:2.54.0 /opt/apache/beam /opt/apache/beam

COPY --from=gcr.io/dataflow-templates-base/python311-template-launcher-base:20230622_RC00 /opt/google/dataflow/python_template_launcher /opt/google/dataflow/python_template_launcher

ARG WORKDIR=/template
WORKDIR ${WORKDIR}

COPY main.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#RUN pip install -e .

ENV FLEX_TEMPLATE_PYTHON_PY_FILE="main.py"

RUN pip check

RUN pip freeze

ENTRYPOINT ["/opt/apache/beam/boot"]