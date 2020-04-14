# Evalytics &middot; [![GitHub license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/eduardogr/evalytics/blob/master/.github/LICENSE) [![Python](https://img.shields.io/badge/Python-v3.6%2B-blue)]() [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/eduardogr/evalytics/blob/master/.github/CONTRIBUTING.md) [![Build Status](https://travis-ci.org/eduardogr/evalytics.svg?branch=master)](https://travis-ci.org/eduardogr/evalytics) [![codecov](https://codecov.io/gh/eduardogr/evalytics/branch/master/graph/badge.svg)](https://codecov.io/gh/eduardogr/evalytics)

The objective of this project is to manage the Performance Evaluation Cycle of a company.

## :bookmark_tabs: Table of Contents

0. [Setting up Evalytics project](#wrench-setting-up-evalytics-project)
0. [Setting up Evalytics config](#pencil-setting-up-evalytics-config)
0. [Running evalytics](#rocket-running-evalytics)
0. [Evalytics files examples](#open_file_folder-evalytics-files-examples)

## :wrench: Setting up Evalytics project

### Create a Google project :zap:

Just access to [Google APIs](https://console.developers.google.com/).

  - Or [click here](https://console.developers.google.com/projectcreate) for a quick project creation.

### Create credentials for your project :key:

Once you have created your project, you can create your project's credentials.

To manage project's credentials you have the section [api/credentials](https://console.developers.google.com/apis/credentials) within [Google APIs](https://console.developers.google.com/). But if this is your first credentials creation you better follow these steps:

  - First, you have to create the [consent](https://console.developers.google.com/apis/credentials/consent) for your project
  - Once the consent is already created and you have a name for you google app you can create your credentials:
      - Go to *+ Create Credentials* and select *OAuth ID client*
      - Or access to [api/credentials/oauthclient](https://console.developers.google.com/apis/credentials/oauthclient)
      - The OAuth client type is *other* and choose the name you prefer :smiley:

You have already created your credentials! :fireworks:

Just place them in a `credentials.json` file in the root of this repository. :heavy_exclamation_mark::heavy_exclamation_mark:

### Enable APIs :books:

You can see where you have to access for each google api in the doc [google apis usage](doc/google-apis/usage.md)

### Generating your token.pickle :unlock:

To authenticate us we have to send a token.pickle to Google APIs, this token.pickle is generated using the file credentials.json.

To generate this we have the make target google-auth, so, you just have to tun

  - `make google-auth`



:warning: Credentials files to authenticate yourself are included in our [.gitignore](.gitignore) 

:angel: So, you don't have to worry about that :smiley:

## :pencil: Setting up Evalytics config

There's an [Evalytics config](./config.ini) to help you configure your Evalytics instance:

* *Google*

  - FOLDER: Google Drive folder where files are stored.
  - ORGCHART: Google Spreadsheet where employees are listed. [See the example](./examples/eval-process/0_existing_OrgChart.csv).
  - FORM_MAP: Google Spreadsheet where employees forms are listed by kind of form. [See the example](./examples/eval-process/0_existing_FormMap.csv).

* *Company*

  - DOMAIN: domain of your company, e.g. mycompany.com. This will be used for email delivery.
  - NUMBER_OF_EMPLOYEES: number of employees in your [orgchart file]((./examples/eval-process/0_existing_OrgChart.csv))

Fill the [Evalytics config](./config.ini) to let it work properly.

## :rocket: Running evalytics

Preparing local environment to run evalytics:

### Prerequisites to running it locally

From the root path of this project:

```
python3 -m venv env
source env/bin/activate
pip install -r evalytics/requirements/dev.txt
export PYTHONPATH=`pwd`
make google-auth
```

Check values of [evalytics config](./config.ini)

### Running Evalytics server

Using docker:

```
make build
make run-server
```

Using Python virtual envs:

```
python3 evalytics/server.py
```

### Making requests to Evalytics

API Endpoints:

  - /setup
  - /reviewers
  - /sendmail

Using provided Python client:

```
python3 evalytics/client.py setup
python3 evalytics/client.py reviewers
python3 evalytics/client.py reviewers --stats
python3 evalytics/client.py send_evals
python3 evalytics/client.py send_evals --retry
python3 evalytics/client.py send_evals --whitelist
```

or using cURL directly:
```
curl -X POST localhost:8080/setup | json_pp
curl localhost:8080/reviewers | json_pp
curl -X POST localhost:8080/sendmail -d '.....' | json_pp (better use the Python client for this endpoint to avoid write all of the data that has to be sent :) )

```

## :open_file_folder: Evalytics files examples

```
examples/
        eval-process/: Example documents for each eval subprocess
        google-api-client/: Example clients for each google api that we use
```
