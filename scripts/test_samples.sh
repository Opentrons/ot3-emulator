#!/usr/bin/env bash
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
SAMPLE_PATHS=`(cd ${SCRIPT_DIR}/../ && find samples -name "*.json" -or -name "*.yaml")`
FAILURE="FALSE"

for val in ${SAMPLE_PATHS}; do
    abs_path=`(cd ${SCRIPT_DIR}/../ && echo ${PWD}/${val})`
    (cd ${SCRIPT_DIR}/../ && make generate-compose-file file_path=${abs_path}) > /dev/null

    if [ $? -ne 0 ]; then
      FAILURE="TRUE"
      printf "\n${val} failed\n\n"
    fi
done

if [ ${FAILURE} == "TRUE" ]; then
  echo "Not all sample files are valid. Exiting with error code 1"
  exit 1
fi

echo "All sample files generated compose files successfully"
