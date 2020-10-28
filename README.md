[![Build Status](https://github.com/maxisme/idmyteam-client/workflows/ID%20My%20Team%20Client/badge.svg)](https://github.com/maxisme/idmyteam-client/actions)


[Server Code](https://github.com/maxisme/idmyteam-server)


# Local environment

## `pre-commit`
```
$ pip install pre-commit
$ pre-commit install
```

to test:
```
$ pre-commit run --all-files
```

## create venv
```
python3 -m venv .venv
```


___

#### requirements.txt
```
pipdeptree | grep -P '^\w+' > web/requirements.txt