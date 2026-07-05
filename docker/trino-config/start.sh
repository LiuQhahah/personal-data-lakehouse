#!/bin/bash

if [ "$TRINO_ENV" = "coordinator" ]; then
    exec /usr/lib/trino/bin/launcher run /etc/trino/coordinator.properties
elif [ "$TRINO_ENV" = "worker" ]; then
    exec /usr/lib/trino/bin/launcher run /etc/trino/worker.properties
else
    # 默认模式
    exec /usr/lib/trino/bin/launcher run
fi
