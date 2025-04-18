# OpenCTI External Ingestion Connector IBM X-Force Premier Threat Intelligence Services

<!--
General description of the connector
* What it does
* How it works
* Special requirements
* Use case description
* ...
-->

Table of Contents

- [OpenCTI External Ingestion Connector IBM X-Force Premier Threat Intelligence Services](#opencti-external-ingestion-connector-ibm-x-force-premier-threat-intelligence-services)
  - [Introduction](#introduction)
  - [Installation](#installation)
    - [Requirements](#requirements)
  - [Configuration variables](#configuration-variables)
    - [OpenCTI environment variables](#opencti-environment-variables)
    - [Base connector environment variables](#base-connector-environment-variables)
    - [Connector extra parameters environment variables](#connector-extra-parameters-environment-variables)
  - [Deployment](#deployment)
    - [Docker Deployment](#docker-deployment)
    - [Manual Deployment](#manual-deployment)
  - [Usage](#usage)
  - [Behavior](#behavior)
  - [Debugging](#debugging)
  - [Additional information](#additional-information)

## Introduction

X-Force Threat Intelligence delivers insights to help clients improve their security posture. X-Force Threat Intelligence combines IBM security operations telemetry, research, incident response investigations, commercial data, and open sources to aid clients in understand emerging threats and quickly make informed security decisions.

IBM X-Force offers a TAXII 2.1 Server to access IBM X-Force Premium Threat Intelligence (XTI) Reports and Indicators of Compromise.

## Installation

### Requirements

- OpenCTI Platform >= 6...

## Configuration variables

There are a number of configuration options, which are set either in `docker-compose.yml` (for Docker) or
in `config.yml` (for manual deployment).

### OpenCTI environment variables

Below are the parameters you'll need to set for OpenCTI:

| Parameter     | config.yml | Docker environment variable | Mandatory | Description                                          |
|---------------|------------|-----------------------------|-----------|------------------------------------------------------|
| OpenCTI URL   | url        | `OPENCTI_URL`               | Yes       | The URL of the OpenCTI platform.                     |
| OpenCTI Token | token      | `OPENCTI_TOKEN`             | Yes       | The default admin token set in the OpenCTI platform. |

### Base connector environment variables

Below are the parameters you'll need to set for running the connector properly:

| Parameter       | config.yml      | Docker environment variable | Default         | Mandatory | Description                                                                                |
|-----------------|-----------------|-----------------------------|-----------------|-----------|--------------------------------------------------------------------------------------------|
| Connector ID    | id              | `CONNECTOR_ID`              |                 | Yes       | A unique `UUIDv4` identifier for this connector instance.                                  |
| Connector Type  | type            | `CONNECTOR_TYPE`            | EXTERNAL_IMPORT | Yes       | Should always be set to `EXTERNAL_IMPORT` for this connector.                              |
| Connector Name  | name            | `CONNECTOR_NAME`            |                 | Yes       | Name of the connector.                                                                     |
| Connector Scope | scope           | `CONNECTOR_SCOPE`           |                 | Yes       | The scope or type of data the connector is importing, either a MIME type or Stix Object.   |
| Duration Period | duration_period | `CONNECTOR_DURATION_PERIOD` | PT5M            | No        | Determines the time interval between each launch of the connector in ISO 8601, ex: `PT5M`. |
| Log Level       | log_level       | `CONNECTOR_LOG_LEVEL`       | info            | Yes       | Determines the verbosity of the logs. Options are `debug`, `info`, `warn`, or `error`.     |

### Connector extra parameters environment variables

Below are the parameters you'll need to set for the connector:

| Parameter         | config.yml         | Docker environment variable           | Default                    | Mandatory | Description                                                    |
|-------------------|--------------------|---------------------------------------|----------------------------|-----------|----------------------------------------------------------------|
| TAXII Server URL  | taxii_server_url   | `CONNECTOR_IBM_XTI_TAXII_SERVER_URL`  |                            | Yes       | The base URL of the IBM X-Force PTI TAXII Server               |
| TAXII User        | taxii_user         | `CONNECTOR_IBM_XTI_TAXII_USER`        |                            | Yes       | Your TAXII Server username                                     |
| TAXII Password    | taxii_pass         | `CONNECTOR_IBM_XTI_TAXII_PASS`        |                            | Yes       | Your TAXII Server password                                     |
| TAXII Collections | taxii_collections  | `CONNECTOR_IBM_XTI_TAXII_COLLECTIONS` | All authorized collections | No        | Optionally limit ingestion to specified TAXII collections only. This should be a comma-separated list (spaces allowed) of collection IDs, not the names or aliases |
| Observables       | create_observables | `CONNECTOR_IBM_XTI_CREATE_OBSERVABLES`|                            | No        | Optionally control whether to define observables from indicators |

## Deployment

### Docker Deployment

Before building the Docker container, you need to set the version of pycti in `requirements.txt` equal to whatever
version of OpenCTI you're running. Example, `pycti==5.12.20`. If you don't, it will take the latest version, but
sometimes the OpenCTI SDK fails to initialize.

Build a Docker Image using the provided `Dockerfile`.

Example:

```shell
# Replace the IMAGE NAME with the appropriate value
docker build . -t [IMAGE NAME]:latest
```

Make sure to replace the environment variables in `docker-compose.yml` with the appropriate configurations for your
environment. Then, start the docker container with the provided docker-compose.yml

```shell
docker compose up -d
# -d for detached
```

### Manual Deployment

Create a file `config.yml` based on the provided `config.yml.sample`.

Replace the configuration variables (especially the "**ChangeMe**" variables) with the appropriate configurations for
you environment.

Install the required python dependencies (preferably in a virtual environment):

```shell
pip3 install -r requirements.txt
```

Then, start the connector from recorded-future/src:

```shell
python3 main.py
```

## Usage

After Installation, the connector should require minimal interaction to use, and should update automatically at a regular interval specified in your `docker-compose.yml` or `config.yml` in `duration_period`.

However, if you would like to force an immediate download of a new batch of entities, navigate to:

`Data management` -> `Ingestion` -> `Connectors` in the OpenCTI platform.

Find the connector, and click on the refresh button to reset the connector's state and force a new
download of data by re-running the connector.

## Behavior

The IBM XTI connector populates the following entity types from the IBM X-Force TAXII server:
  - Indicators
  - Reports
  - Vulnerabilities
  - Malware

By default, the connector will ingest from all collections your TAXII credentials have access to. If you configure the optional `taxii_collections` setting, then ingestion will be limited to only those specified collections. Once you have configured the required settings, such as the `taxii_server_url`, `taxii_user`, and `taxii_pass`, the connector will ingest from all applicable collections in parallel, so you don't have to wait for each collection to finish ingesting one by one.

Note: some of the collections have a large volume of data. It is expected behavior upon the initial run of the connector for it to run for several hours. After each run, the connector will store information about the last records it retrieved, so upon the next scheduled run of the connector, it will only ingest new records. If the connector runs into any transient issues while ingesting from a collection, it will retry from where it left off. The connector runs every 5 minutes by default, unless otherwise configured; a new run will not start until all ingestion processes have completed.

## Debugging

The connector can be debugged by setting the appropiate log level.
Note that logging messages can be added using `self.helper.connector_logger,{LOG_LEVEL}("Sample message")`, i.
e., `self.helper.connector_logger.error("An error message")`.

<!-- Any additional information to help future users debug and report detailed issues concerning this connector -->

## Additional information

<!--
Any additional information about this connector
* What information is ingested/updated/changed
* What should the user take into account when using this connector
* ...
-->
