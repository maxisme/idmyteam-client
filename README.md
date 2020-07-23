[![Build Status](https://github.com/maxisme/idmyteam-client/workflows/ID%20My%20Team%20Client/badge.svg)](https://github.com/maxisme/idmyteam-client/actions)


[Server Code](https://github.com/maxisme/idmyteam-server)
```
$ git config core.hooksPath .githooks/
$ chmod +x .githooks/*
```

```
nano /etc/dphys-swapfile
```
set:
```
CONF_SWAPSIZE=2048
```

then:
```
dphys-swapfile setup
```

# running
```
$ docker-compose up -d db
$ docker-compose up migrate
```