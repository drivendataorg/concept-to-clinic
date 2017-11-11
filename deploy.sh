#!/bin/bash
set -ex

# use longform git hash as version
VERSION=$(git show -s --format=%H)

pip install --user awscli # install aws cli w/o sudo
pip install --user sceptre # install sceptre cli w/o sudo

export PATH=$PATH:$HOME/.local/bin

# docker login using AWS env vars
eval $(aws ecr get-login --region us-east-1)

# build, tag, push API
docker build -t concept-to-clinic/api:$VERSION --file ./compose/interface/Dockerfile-api .
docker tag concept-to-clinic/api:$VERSION 113913174193.dkr.ecr.us-east-1.amazonaws.com/c2c-api:$VERSION
docker push 113913174193.dkr.ecr.us-east-1.amazonaws.com/c2c-api:$VERSION

# build, tag, push  UI
docker build -t concept-to-clinic/api:$VERSION --file ./compose/interface/Dockerfile-api .
docker tag concept-to-clinic/api:$VERSION 113913174193.dkr.ecr.us-east-1.amazonaws.com/c2c-api:$VERSION
docker push 113913174193.dkr.ecr.us-east-1.amazonaws.com/c2c-api:$VERSION

# build, tag, push prediction
docker build -t concept-to-clinic/api:$VERSION --file ./compose/interface/Dockerfile-api .
docker tag concept-to-clinic/api:$VERSION 113913174193.dkr.ecr.us-east-1.amazonaws.com/c2c-api:$VERSION
docker push 113913174193.dkr.ecr.us-east-1.amazonaws.com/c2c-api:$VERSION

# deploy to AWS
sceptre --dir 'deploy/' --var "APIVersion=$VERSION" --var "UIVersion=$VERSION" --var "PredictionVersion=$VERSION" \
    --var-file=versions.yaml update-stack dev c2c
