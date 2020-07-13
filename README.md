<h1 align="center"> Evalytics </h1> <br>

The Evalytics project aim is to be the platform to support a company's Human Resources team within the Performance Evaluation Cycle.

## :bookmark_tabs: Table of Contents

0. [Introduction](#introduction)
0. [Tech/framework used](#techframework-used)
0. [Performance Evaluation Cycle](#book-performance-evaluation-cycle)
0. [API reference](#book-api-reference)
0. [Setting up Evalytics config](#pencil-setting-up-evalytics-config)
0. [Hosting Evalytics locally](#computer-hosting-evalytics-locally)
0. [Google setup for Evalytics](#wrench-google-setup-for-evalytics)
0. [Contributing](#family-contributing)
0. [License](#page_with_curl-license)

# Introduction 
[![Build Status](https://travis-ci.org/eduardogr/evalytics.svg?branch=master)](https://travis-ci.org/eduardogr/evalytics)
[![codecov](https://codecov.io/gh/eduardogr/evalytics/branch/master/graph/badge.svg)](https://codecov.io/gh/eduardogr/evalytics)
[![Python](https://img.shields.io/badge/Python-v3.6%2B-blue)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/eduardogr/evalytics/blob/master/.github/CONTRIBUTING.md)
[![GitHub license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/eduardogr/evalytics/blob/master/.github/LICENSE)  

This project defines the Performance Evaluation Cycle as a process **_platform-free_**.

**What does _platform-free_ mean?**

It means that Evalytics is adaptable to the different ecosystems of the different companies depending on the stack of technology they use

> e.g. Google, Microsoft, Slack, own webhooks or services, ... etc 

Satisfying heterogeneous requirements and adapting them in a single project where we can choose the technological stack we want to use.

**Is your company's technology stack covered with Evalytics?**

If your company's technology stack is not satisfied with Evalytics, please, let us know and open a [feature request](https://github.com/eduardogr/evalytics/issues/new?assignees=&labels=&template=feature_request.md).

## Tech/framework used

### Built with
  - Python 3.6+
  - [Tornado Web Server](https://www.tornadoweb.org/en/stable/)
  - [yaml](https://yaml.org/) for app configuration
  - **docker** for containerization and **docker-compose** for defining and running docker containers

### Integrated with
  - Google
    - Google Drive
    - Google Spreadsheets
    - Google Docs
    - Gmail
  - Slack

## :book: Performance Evaluation Cycle

### Glossary :speech_balloon:

- **Employee**: any person that participate in the process reviewing or being reviewed.
- **Direct report**: from the manager's perspective, an employee that belongs to a team
- **Manager**: an employee that leads a group of employees, their direct reports.
- **Peer**: an employee that co-work with another but with no management relationship.
- **Survey**: Set of questions to answer. It is related to the area of employees and the relationship of employees.
- **Eval reports**: Set of responses and data extracted from employee surveys.

### Types of evaluations

- 180º
    - Employees are going to review theirselves, their manager and their direct reports (if they have it).
- 360º
    - 180º evaluation + evaluation of their peers.

### Phases of a Performance Evaluation Cycle

- Peers assignment (just for 360º evaluations)
    - Here managers are going to decide who is going to review each of their direct reports.

- Review phase
    - Reviewers gonna review.

- End phase
    - Gathering surveys' responses and extracting data from them.
    - Sharing **_eval reports_** with managers

## :book: API reference

### GET /employees

Retrieves the list of employees

```
> GET /employees HTTP/<http-version>
> 
< HTTP/<http-version> 200 OK
< Server: TornadoServer/6.0.4
< Content-Type: application/json; charset=UTF-8
{
  "success" : true,
  "response" : {
    "employees" : [
      {
        "manager" : "employee_1_manager",
        "uid" : "employee_1",
        "mail" : "employee_1@company.com",
        "area" : "area 1"
      },
      ...
      ...
      {
        "manager" : "employee_N_manager",
        "uid" : "employee_N",
        "mail" : "employee_N@company.com",
        "area" : "area 1"
      }
    ]
  }
}
```

### GET /surveys

Retrieves the list of surveys

```
> GET /surveys HTTP/<http-version>
>
< HTTP/<http-version> 200 OK
< Server: TornadoServer/6.0.4
< Content-Type: application/json; charset=UTF-8
{
  "success" : true,
  "response" : {
    "surveys" : {
      "Area of Employee type 1" : {
        "SELF" : "https://survey.url.com/area_type_1/self",
        "PEER_TO_PEER" : "https://survey.url.com/area_type_1/peer_peer",
        "MANAGER_PEER" : "https://survey.url.com/area_type_1/manager_peer",
        "PEER_MANAGER" : "https://survey.url.com/area_type_1/peer_manager"
      },
      ...
      ...
      "Area of Employee type N" : {
        "SELF" : "https://survey.url.com/area_type_N/self",
        "PEER_TO_PEER" : "https://survey.url.com/area_type_N/peer_peer",
        "MANAGER_PEER" : "https://survey.url.com/area_type_N/manager_peer",
        "PEER_MANAGER" : "https://survey.url.com/area_type_N/peer_manager"
      }
    }
  }
}
```

### GET /reviewers

Retrieves the list of reviewers

```
> GET /reviewers HTTP/<http-version>
> 
< HTTP/<http-version> 200 OK
< Server: TornadoServer/6.0.4
< Content-Type: application/json; charset=UTF-8

{
  "success" : true,
  "response" : {
    "reviewers" : [
      {
        "employee" : {
          "manager" : "employee_1_manager",
          "uid" : "employee_1",
          "mail" : "employ_1@company.com",
          "area" : "area 1"
        },
        "evals" : [
          {
            "form" : "https://survey.url.com/area_type_1/self",
            "reviewee" : "employee_1",
            "kind" : "SELF"
          },
          ...
          ...
          {
            "form" : "https://survey.url.com/area_type_1/peer_manager",
            "kind" : "PEER_MANAGER",
            "reviewee" : "employee_1_manager"
          }
         ]
      },
      ...
      ...
    ]
  }
}
```

### POST /communications

Sends communications

### GET /status

Retrieves the status of the current eval process

```
> GET /status HTTP/<http-version>
> 
< HTTP/<http-version> 200 OK
< Server: TornadoServer/6.0.4
< Content-Type: application/json; charset=UTF-8

{
  "success" : true,
  "response" : {
    "status" : {
      "inconsistent" : {
        "employee_1" : {
          "reviewee_X" : {
            "kind" : "MANAGER_PEER",
            "reason" : "WRONG_REPORTER: 'reviewee_X' is not one of expected reporters. Reporters: [<list of reporters>]",
          }
        }
      },
      "pending" : [
        {
          "evals" : [<list of evals>],
          "employee" : {
            "uid" : "employee_1",
            "area" : "area 1",
            "mail" : "ruben.mazariegosdelrey@tuenti.com",
            "manager" : "aaron"
          }
        },
      ],
      "completed": {
        "employee_X" : {
          "reviewee_A" : {
            "kind" : "eval kind"
          },
          ...
          ...
          "reviewee_Z" : {
            "kind" : "eval kind"
          }
        },
        "employee_Y" : {
          "reviewee_G" : {
            "kind" : "eval kind"
          },
          ...
          ...
          "reviewee_R" : {
            "kind" : "eval kind"
          }
        }
      }
    }
  }
}
```

### GET /evalreports

Retrieve eval reports

### POST /evalreports

Generate eval reports

## :pencil: Evalytics Config

There's an [Evalytics config](./config.yaml.example) to help you configure your Evalytics instance:

* **Eval process**

  - id: Evalytics process ID.
  - due_date: Evalytics provider for communications delivery. e.g. gmail.
  - feature_disabling:

* **Providers**

  - storage: Evalytics provider for storage. e.g. google drive.
  - communication_channel: Evalytics provider for communications delivery. e.g. gmail.
  - forms_platform: Evalytics provider for surveys. e.g. google forms.

* **Company**

  - domain: domain of your company, e.g. mycompany.com. This will be used for email delivery.
  - number_of_employees: number of employees in your [orgchart file](./examples/eval-process/0_existing_OrgChart.csv)

* **Gmail provider**

  - mail_subject: Email subject for eval delivery communications.
  - reminder_mail_subject: Email subject for reminder communications.

* **Google Drive provider**

  - folder: Google Drive folder where files are stored.
  - org_chart: Google Spreadsheet where employees are listed. [See an example](./examples/eval-process/0_existing_OrgChart.csv).
  - form_map: Google Spreadsheet where employees forms are listed by kind of form. [See an example](./examples/eval-process/0_existing_FormMap.csv).
  - form_responses_folder: Google Drive folder where response files are stored.
  - eval_report_template_id: Google Document ID where we've defined our eval report template. [See an example](./examples/eval-process/0_existing_EvalReportTemplate.md).
  - eval_report_prefix_name: Prefix for eval reports documents we are going to create.
      - e.g. if prefix is 'Eval Report: ', files generated for employee1 and employee2 are going to have titles; 'Eval Report: employee1' and 'Eval Report: employee2' 

Create a config.yaml file from [config.yaml.example](./config.yaml.example) with correct values for each key to let Evalytics work properly.

## :computer: Hosting Evalytics locally

### :rocket: Running the Evalytics server

Preparing local environment to run Evalytics:

#### Prerequisites to running it locally

##### Using make + docker-compose

Install make and docker-compose

##### Using Python virtual envs

From the root path of this project:

```
./setup.sh
```

#### Running Evalytics server

##### Using make + docker-compose

```
make build
make up
```

##### Using Python virtual envs

```
python3 server.py
```

### :rocket: Making requests to the Evalytics server

#### Possible commands
  - employees
  - surveys
  - reviewers
    > **options**: *--stats*
  - send_evals
    > **options**: *--retry*, *--whitelist*
  - send_due_date_comm
    > **options**: *--retry*, *--whitelist*
  - send_reminders
    > **options**: *--retry*, *--whitelist*
  - status
    > **options**: *--inconsistent-files*
  - reports
    > **options**: *--dry-run*, *--whitelist*

#### Using make + docker-compose

Using make target provided

```
make request ARGS='<command> <options>'
```

#### Using Python virtual envs

Using provided Python client:

```
python3 client.py <commnad> <options>
```

#### Using cURL directly:

```
curl -X HTTP_VERB localhost:8080/<endpoint> | json_pp
```

## :wrench: Google setup for Evalytics

### Google API credentials

#### Create a Google project :zap:

Just access to [Google APIs](https://console.developers.google.com/).

  - Or [click here](https://console.developers.google.com/projectcreate) for a quick project creation.

#### Create credentials for your project :key:

Once you have created your project, you can create your project's credentials.

To manage project's credentials you have the section [api/credentials](https://console.developers.google.com/apis/credentials) within [Google APIs](https://console.developers.google.com/). But if this is your first credentials creation you better follow these steps:

  - First, you have to create the [consent](https://console.developers.google.com/apis/credentials/consent) for your project
  - Once the consent is already created and you have a name for you google app you can create your credentials:
      - Go to *+ Create Credentials* and select *OAuth ID client*
      - Or access to [api/credentials/oauthclient](https://console.developers.google.com/apis/credentials/oauthclient)
      - The OAuth client type is *other* and choose the name you prefer :smiley:

You have already created your credentials! :fireworks:

Just place them in a `credentials.json` file in the root of this repository. :heavy_exclamation_mark::heavy_exclamation_mark:

#### Enable Google APIs :books:

You can see where you have to access for each google api in the doc [google apis usage](doc/google-apis/usage.md)

#### Generating your token.pickle :unlock:

To authenticate us we have to send a token.pickle to Google APIs, this token.pickle is generated using the file credentials.json.

To generate this we have the make target google-auth, so, you just have to tun

  - `make google-auth`


:warning: Credentials files to authenticate yourself are included in our [.gitignore](.gitignore)

:angel: So, you don't have to worry about that :smiley:

### Evalytics google files examples

```
examples/
        eval-process/: Example documents for each eval subprocess
        google-api-client/: Example clients for each google api that we use
```

## :family: Contributing

[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/eduardogr/evalytics/blob/master/.github/CONTRIBUTING.md)

Contributions are welcome! Please see our [Contributing Guide](<https://github.com/eduardogr/evalytics/blob/master/.github/CONTRIBUTING.md>) for more
details.

## :page_with_curl: License

This project is licensed under the [Apache license](https://github.com/eduardogr/evalytics/blob/main/LICENSE).
