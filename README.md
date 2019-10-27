[![Build Status](https://jenk.ml/job/idmyteam-client/badge/icon)](https://jenk.ml/job/idmyteam-client/)


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
