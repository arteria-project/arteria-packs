#!/bin/bash

# Simple script that should be executed on a biotank when we want to compress a
# runfolder to be archived to PDC via TSM. The runfolder to archive is expected
# to be a folder full of symlinks pointing to real source folder. 

set -e
set -o pipefail 

# The full path to the runfolder that we want to archive.
RUNFOLDER=$1

RUNFOLDER_NAME=$(basename ${RUNFOLDER})

# The exclude pattern is for everything we do not want to pack, and is configurable 
# upstreams. It should hopefully look something like the following. 
# EXCLUDE="^Config|^InterOp|^SampleSheet.csv|^Unaligned|^runParameters.xml|^RunInfo.xml"
# Escaping various quotes can be messy though. 
EXCLUDE=$2

cd ${RUNFOLDER}

# If the normal archive workflow is re-run then the tar ball shouldn't exist anymore because
# either the linked directory structory will be re-created from scratch, or the workflow
# should have aborted at an earlier stage because the archive dir already exists. 
# Still, just in case, abort if it is found. 
if [ -f ./${RUNFOLDER_NAME}.tar.gz ]; then
  echo "Gziped archive file ${RUNFOLDER_NAME}.tar.gz already exists. Manual intervention required."
  exit 1
fi

# Create list of root links to include in the compressed part of the archive.
# Should have a couple of file patterns excluded from the config. 
# 
# NB: As this works now the excluded files from the tar ball must be a link
# in the root folder. If we want to be able to exclude files deeper in the 
# directory tree then we need to redo this step, as well as the tar and 
# removal step. 
ls -A | egrep -v ${EXCLUDE} > ./.links-to-pack

# Pack everything together. Compressing is perhaps not strictly necessary, but it 
# will save some space for primarily the log files. We want to derefence symlinks, 
# as normal procedure is to archive a runfolder full with symlinks to the files 
# that should be uploaded.
tar -h -T ./.links-to-pack -c -z -f ./${RUNFOLDER_NAME}.tar.gz 

# Remove all symlinks that we include in the tar ball 
for link in `cat ${RUNFOLDER}/.links-to-pack`; do 
    rm ${RUNFOLDER}/${link}
done

