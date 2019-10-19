#!/bin/bash
# for jenkins ssh:
# $ visudo
# jenk ALL = NOPASSWD: /bin/bash /root/idmyteam-client/deploy.sh

cd /root/idmyteam-client

git checkout master
git fetch &> /dev/null
diffs=$(git diff master origin/master)

if [ ! -z "$diffs" ]
then
    echo "Pulling code from GitHub..."
    git pull origin master

    supervisorctl restart webpanel:*
else
    echo "Already up to date"
fi