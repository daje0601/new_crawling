#!/bin/sh

json="{\"text\": \"완료되었습니다. \"}"
echo "json : " $json

my_slack_webhook="https://hooks.slack.com/services/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"

curl -X POST -H 'Content-type: application/json' --data "$json" $my_slack_webhook
