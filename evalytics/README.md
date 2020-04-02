# evalytics


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

