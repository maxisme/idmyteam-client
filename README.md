[![Build Status](https://github.com/maxisme/idmyteam-client/workflows/ID%20My%20Team%20Client/badge.svg)](https://github.com/maxisme/idmyteam-client/actions)


[Server Code](https://github.com/maxisme/idmyteam-server)


# Local environment

## `pre-commit`
```
$ pip install pre-commit
$ pre-commit install
```

run manually:
```
$ pre-commit run --all-files
```

## create venv
```
python3 -m venv .venv
```

### Custom `runserver`
```
$ docker-compose up -d db redis
$ cd web
$ python3 manage.py migrate
$ python3 manage.py loaddata test-user.json
$ python3 manage.py runserver
```
You can then login with the credentials `testuser`:`cXJRwjtUiDqAnNxA9Qkb`


___

#### requirements.txt
```
pipdeptree | grep -P '^\w+' > web/requirements.txt
```

#### sass
 - `sass source/stylesheets/index.scss build/stylesheets/index.css`
 - `$FilePath$ $FileNameWithoutExtension$.css` (intelij)
 

### Updating models
```
$ python3 manage.py makemigrations
```