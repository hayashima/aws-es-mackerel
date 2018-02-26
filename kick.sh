#!/usr/bin/env bash

sam local generate-event schedule | sam local invoke PostEsMetrics -t src/template.yaml -n env.json
