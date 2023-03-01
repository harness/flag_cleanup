#!/bin/bash

OUTPUT_FILE=output
# start with base command
CMD="polyglot_piranha "

# add language
if [[ -z ${PLUGIN_LANGUAGE} ]]; then
  echo "missing required parameter language"
  exit 1
fi
CMD="$CMD -l=$PLUGIN_LANGUAGE"

# add path to codebase - defaults to current directory
CMD="$CMD -c ${PLUGIN_PATH_TO_CODEBASE:-.}"

# add path to configurations - defaults to current directory
CMD="$CMD -f ${PLUGIN_PATH_TO_CONFIGURATIONS:-.}"

# cleanup comments - defaults to true
if [ "${PLUGIN_CLEANUP_COMMENTS:-true}" = true ] ; then
    CMD="$CMD --cleanup-comments"
fi

# cleanup comments buffer - defaults to 2
CMD="$CMD --cleanup-comments-buffer ${PLUGIN_CLEANUP_COMMENTS_BUFFER:-2}"

# delete file if empty - defaults to true
if [ "${PLUGIN_DELETE_FILE_IF_EMPTY:-true}" = true ] ; then
    CMD="$CMD --delete-file-if-empty"
fi

# delete consecutive new lines - defaults to true
if [ "${PLUGIN_DELETE_CONSECUTIVE_NEW_LINES:-true}" = true ] ; then
    CMD="$CMD --delete-consecutive-new-lines"
fi

# add in all substitutions which should be in the format variable=value e.g. flag_name=my_flag,treated_as=true
IFS=', ' read -r -a substitutions <<< "$PLUGIN_SUBSTITUTIONS"
for element in "${substitutions[@]}"
do
    CMD="$CMD -s $element"
done

echo $CMD

# run as dry run - defaults to false
if [ "${PLUGIN_DRY_RUN}" = true ] ; then
    CMD="$CMD --dry-run"
fi

# place output in output file
CMD="$CMD --path-to-output-summary $OUTPUT_FILE"

# run the command
$CMD

# print output if running debug mode
if [ "${PLUGIN_DEBUG}" = true ] ; then
    cat $OUTPUT_FILE
fi
rm $OUTPUT_FILE