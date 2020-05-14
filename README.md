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

* **Google**

  - folder: Google Drive folder where files are stored.
  - org_chart: Google Spreadsheet where employees are listed. [See an example](./examples/eval-process/0_existing_OrgChart.csv).
  - form_map: Google Spreadsheet where employees forms are listed by kind of form. [See an example](./examples/eval-process/0_existing_FormMap.csv).
  - form_responses_folder: Google Drive folder where response files are stored.
  - eval_report_template_id: Google Document ID where we've defined our eval report template. [See an example](./examples/eval-process/0_existing_EvalReportTemplate.md).
  - eval_report_prefix_name: Prefix for eval reports documents we are going to create.
      - e.g. if prefix is 'Eval Report: ', files generated for employee1 and employee2 are going to have titles; 'Eval Report: employee1' and 'Eval Report: employee2' 

* **Company**

  - domain: domain of your company, e.g. mycompany.com. This will be used for email delivery.
  - number_of_employees: number of employees in your [orgchart file](./examples/eval-process/0_existing_OrgChart.csv)

Create a config.ini file from [config.ini.example](./config.ini.example) with correct values for each key to let Evalytics work properly.

## :rocket: Running evalytics

Preparing local environment to run evalytics:

### Prerequisites to running it locally

#### Using make + docker-compose

Install docker-compose 

#### Using Python virtual envs

From the root path of this project:

```
./setup.sh
```

Check values of [evalytics config](./config.ini)

### Running Evalytics server

#### Using make + docker-compose

```
make build
make up
```

#### Using Python virtual envs

```
python3 evalytics/server.py
```

### Making requests to Evalytics

API Endpoints:

  - /setup
  - /reviewers
  - /evaldelivery
  - /status
  - /evalreports

#### Using make + docker-compose

```
make request ARGS='setup'

make request ARGS='reviewers'
make request ARGS='reviewers --stats'

make request ARGS='send_evals'
make request ARGS='send_evals --retry'
make request ARGS='send_evals --whitelist'

make request ARGS='send_reminders'
make request ARGS='send_reminders --retry'
make request ARGS='send_reminders --whitelist'

make request ARGS='status'
make request ARGS='status --inconsistent-files'

make request ARGS='reports'
make request ARGS='reports --dry-run'
make request ARGS='reports --whitelist'
```

#### Using Python virtual envs

Using provided Python client:

```
python3 evalytics/client.py setup

python3 evalytics/client.py reviewers
python3 evalytics/client.py reviewers --stats

python3 evalytics/client.py send_evals
python3 evalytics/client.py send_evals --retry
python3 evalytics/client.py send_evals --whitelist

python3 evalytics/client.py send_reminders
python3 evalytics/client.py send_reminders --retry
python3 evalytics/client.py send_reminders --whitelist

python3 evalytics/client.py status
python3 evalytics/client.py status --inconsistent-files

python3 evalytics/client.py reports
python3 evalytics/client.py reports --dry-run
python3 evalytics/client.py reports --whitelist
```

#### Using cURL directly:

```
curl -X POST localhost:8080/setup | json_pp
curl localhost:8080/reviewers | json_pp
curl -X POST localhost:8080/evaldelivery -d '.....' | json_pp (better use the Python client for this endpoint to avoid write all of the data that has to be sent :) )

```

## :open_file_folder: Evalytics files examples

```
examples/
        eval-process/: Example documents for each eval subprocess
        google-api-client/: Example clients for each google api that we use
```
