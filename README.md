# evalytics [![Build Status](https://travis-ci.org/eduardogr/evalytics.svg?branch=master)](https://travis-ci.org/eduardogr/evalytics) [![codecov](https://codecov.io/gh/eduardogr/evalytics/branch/master/graph/badge.svg)](https://codecov.io/gh/eduardogr/evalytics)

This project proposal is to manage the evaluation cycle for a company.

## Setting up the project 

### :zap: Create a Google project

Just access to [Google APIs](https://console.developers.google.com/).

  - Or [click here](https://console.developers.google.com/projectcreate) for a quick project creation.

### :key: Create credentials for your project

Once you have created your project, you can create your project's credentials.

To manage project's credentials you have the section [api/credentials](https://console.developers.google.com/apis/credentials) within [Google APIs](https://console.developers.google.com/). But if this is your first credentials creation you better follow these steps:

  - First, you have to create the [consent](https://console.developers.google.com/apis/credentials/consent) for your project
  - Once the consent is already created and you have a name for you google app you can create your credentials:
      - Go to *+ Create Credentials* and select *OAuth ID client*
      - Or access to (api/credentials/oauthclient)[https://console.developers.google.com/apis/credentials/oauthclient]
      - The OAuth client type is *other* and choose the name you prefer :smiley:

So, you have already created your credentials! 

You just have to placed the `credentials.json` file in the root of this repository.

### :books: Enable APIs

You can see where you have to access for each google api in the doc [google apis usage](doc/google-apis/usage.md)

### :unlock: Generating your token.pickle

To authenticate us we have to send a token.pickle to Google APIs, this token.pickle is generated using the file credentials.json.

To generate this we have the make target google-auth, so, you just have to tun

  - `make google-auth`



:warning: Credentials files to authenticate yourself are included in our (.gitignore)[.gitignore] 

:angel: So, you don't have to worry about that :smiley:

