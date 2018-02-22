#!/usr/bin/env bash

AWS_REGION=ap-northeast-1 \
    sam local generate-event schedule \
    | sam local invoke --template src/template.yaml --env-vars env.json
