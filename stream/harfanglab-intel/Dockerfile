FROM python:3.11-alpine
ENV CONNECTOR_TYPE=STREAM

# Copy the connector
COPY src /opt/opencti-harfanglab-intel

# Install Python modules
# hadolint ignore=DL3003
RUN apk update && apk upgrade && \
    apk --no-cache add git build-base libmagic libffi-dev libxml2-dev libxslt-dev

RUN cd /opt/opencti-harfanglab-intel && \
    pip3 install "setuptools~=78.1.0" && pip3 install --no-cache-dir -r requirements.txt && \
    apk del git build-base
# explicit setuptools version due to https://github.com/OpenCTI-Platform/connectors/issues/3742

# Expose and entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
