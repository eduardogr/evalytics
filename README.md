# evalytics [![Build Status](https://travis-ci.org/eduardogr/evalytics.svg?branch=master)](https://travis-ci.org/eduardogr/evalytics) [![codecov](https://codecov.io/gh/eduardogr/evalytics/branch/master/graph/badge.svg)](https://codecov.io/gh/eduardogr/evalytics)

This project proposal is to manage the evaluation cycle for a company

## Usage

Preparing local environment to run evalytics:

```
# Could be env=dev for development
make build env=prod 
make google-auth
make run-server
# If you are developing, for reload code within docker container
make run  stop-server && make start-server 
```

Requesting evalytics:

```
curl -s localhost:8080/start -d 'id=201' | json_pp
{
   "message" : "You have started an evaluation process",
   "id" : "201",
   "success" : true
}
```

## Examples

```
examples/
        eval-process/: Example documents for each eval subprocess
        google-api-client/: Example clients for each google api that we use
```


## Authentication

### Google authentication

Note that, if you are going to use google apis you have to run `make google-auth` to obtain
your token.pickle using credentials.json.

See our [google apis usage](doc/google-apis/usage.md) doc for more information.
