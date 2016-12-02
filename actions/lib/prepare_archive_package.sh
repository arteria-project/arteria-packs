#!/bin/bash

# Simple script that should be executed on a biotank when we want to prepare a
# runfolder to be archived to PDC via TSM.

set -e

# The full path to the runfolder that we want to archive.
RUNFOLDER=$1

RUNFOLDER_NAME=$(basename ${RUNFOLDER})

# The exclude pattern is for everything we do not want to pack, and is configurable 
# upstreams. It should hopefully look something like the following. 
# EXCLUDE="^./Config|^./InterOp|^./SampleSheet.csv|^./Unaligned|^./Data|^./Thumbnail_Images|^./runParameters.xml|^./RunInfo.xml"
# Escaping various quotes can be messy though. 
EXCLUDE=$2

cd ${RUNFOLDER}

# TODO: Shall we upload it when it exists?
if [ -f ./${RUNFOLDER_NAME}.tar.gz ]; then
  echo "Gziped archive file ${RUNFOLDER_NAME}.tar.gz already exists. Manual intervention required."
  exit 1
fi

# Create list of files to include in the compressed part of the archive.
# Should have a couple of file patterns excluded from the config.
# Note that we're only adding the files, and not the directories, because
# it would cause tar to return with a failure code when removing directories
# before files in subdirs have been removed. (And if we use the exclude features
# from tar instead then it will always add "." which causes its own problems
# as it can't be removed.)
find . -type f -print | egrep -v ${EXCLUDE} > ./.files-to-pack

# Pack everything together and then remove them at the same time. More
# efficiently space wise than removing them afterwards. Compressing is perhaps
# not strictly necessary, but it will save some space for primarily the log files.
tar -T ./.files-to-pack -c -z -f ./${RUNFOLDER_NAME}.tar.gz --remove-files

# Optional step: remove all the empty dirs that will now exist due to the
# removed files. When extracting the archive the dirs with files will be
# created. Obviously any dirs without any files will be lost. Also note
# that this will change the timestamp on these newly created dirs, but I'm
# guessing that is OK.
find . -type d -empty -delete
