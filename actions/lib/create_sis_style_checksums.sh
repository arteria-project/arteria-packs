#!/bin/bash

set -o errexit

export FOLDER=$1
export INCLUDE_FILE=$2
export OUTPUT_FILE=$3
export FOLDER_NAME=$(basename $FOLDER)

pushd $FOLDER/.. > /dev/null

if [ ! -d "$FOLDER/MD5" ];
then 
  mkdir ${FOLDER}/MD5 
fi

rsync -vrktp --dry-run --chmod=Dg+sx,ug+w,o-rwx --prune-empty-dirs --include-from $INCLUDE_FILE ${FOLDER} /tmp | grep $FOLDER_NAME | grep -v "\/$" | xargs -0 -d"\n" md5sum > $FOLDER/MD5/$OUTPUT_FILE

popd > /dev/null
