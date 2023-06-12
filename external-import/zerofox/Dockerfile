FROM python:3.11-alpine

# Copy the connector
COPY src /opt/opencti-connector-zerofox

# Install Python modules
# hadolint ignore=DL3003
RUN apk update && \
    apk --no-cache add git build-base libmagic libffi-dev libxml2-dev libxslt-dev && \
    cd /opt/opencti-connector-zerofox && \
    pip3 install --no-cache-dir -r requirements.txt && \
    apk del git build-base

# Expose and entrypoint
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]