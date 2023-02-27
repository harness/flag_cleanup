#!/bin/bash

if [[ -z ${PLUGIN_ARGS} ]]; then
  echo "missing required parameter args"
  exit 1
fi

polyglot_piranha $PLUGIN_ARGS -j output
if [ "${PLUGIN_DEBUG}" = true ] ; then
    cat output
fi
rm output