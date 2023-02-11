# Run Gitlab webhook inside docker container

## Docker compose example

```yaml
version: "3.3"

services:
  app:
    [ ... ]
  webhook:
    restart: unless-stopped
    image: mywebhook
    ports:
      - 8888:80
    volumes:
      # Mount the configuration file (see below)
      - ./config/config.json:/hook/config.json
      # Mount the repositories to be updated
      - /opt/repo1:/opt/repo1
      - /opt/repo2:/opt/repo2
      ...
      # Mount the deploy keys (needed for private repos)
      - ./config/.ssh:/root/.ssh
      # Mount the docker socket
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
        TOKEN: supersecrettoken
        BRANCH: main
        POST_SCRIPT: docker-compose restart app
```


## Environment parameters

Parameters            | Second Header
------------          | -------------
TOKEN*                | Gilab token
BRANCH*               | Git branch
COMPOSE_PROJECT_NAME  | docker-compose base dir (if use *docker-compose* in POST_SCRIPT)
PRE_SCRIPT            | Run script before git pull
POST_SCRIPT           | Run script after git pull (if launch *docker-compose exec* don't forget -T parameter)

 ** *Required parameters **

 ## Hook Configuration file

The configuration file provides the list of repositories that will be updated when the hook runs. The local repository paths must be provided as volumes mounted in the container (see the docker compose file example above). 
 
```yaml
{
  "LOCAL_REPO_PATHS": {
     "repo_name_1": "/opt/repo1",
     "repo_name_2": "/opt/repo2"
     ...
  }
}
```



