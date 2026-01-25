#!/bin/sh

# Write start timestamp
START_TIME=$(date +%s)
echo "{\"start_time\": $START_TIME, \"uptime_seconds\": 0}" > /usr/share/nginx/html/uptime.json

# Update uptime every minute in background
(while true; do
    CURRENT_TIME=$(date +%s)
    UPTIME=$((CURRENT_TIME - START_TIME))
    echo "{\"start_time\": $START_TIME, \"uptime_seconds\": $UPTIME}" > /usr/share/nginx/html/uptime.json
    sleep 60
done) &

# Start nginx
exec nginx -g "daemon off;"
