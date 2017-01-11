#!/usr/bin/env python

import os, sys, shutil, argparse

def verify_src(srcdir, threshold = None):
  if not os.path.exists(srcdir) or not os.path.isdir(srcdir):
    print("Runfolder {} is not a directory and/or doesn't exist. Aborting.".format(srcdir))
    sys.exit(1)

  unaligned_link = os.path.join(srcdir, "Unaligned")
  unaligned_dir = os.path.abspath(unaligned_link)

  if not os.path.exists(unaligned_link) or not os.path.islink(unaligned_link): 
    print("Expected link {} doesn't seem to exist or is broken. Aborting.".format(unaligned_link))
    sys.exit(1)
  elif not os.path.exists(unaligned_dir) or not os.path.isdir(unaligned_dir): 
    print("Expected directory {} doesn't seem to exist. Aborting.".format(unaligned_dir))
    sys.exit(1) 
  else:
    counter = 0

    for root, dirs, files in os.walk(unaligned_dir):
      for file in files: 
        if file.lower().endswith(".fastq.gz"):
          counter = counter + 1
  
    if threshold and counter < threshold: 
        print("We found only {} files that seems to be FASTQ files. Expecting at least {} files. Looks suspicious; aborting.".format(counter, threshold))
        sys.exit(1)

def verify_dest(destdir, remove=False): 
  if os.path.exists(destdir):
    if remove: 
      print("Archive directory {} already exists. Operator requested to remove it.".format(destdir))
      shutil.rmtree(destdir)
    else: 
      print("Archive directory {} already exists. Aborting.".format(destdir))
      sys.exit(1)

def create_dest(srcdir, destdir, exclude = None): 
  os.makedirs(destdir)

  for entry in os.listdir(srcdir):
    if not entry in exclude: 
      os.symlink(os.path.join(srcdir, entry), os.path.join(destdir, entry))
 
  print("Archive directory {} created successfully.".format(destdir))

def str2bool(val): 
    return val.lower() in ("yes", "true", "1")  

if __name__ == "__main__": 
  parser = argparse.ArgumentParser(description="Takes a runfolder's path as an argument and creates a copy of it with symlinks\n"\
                                               "as its content, suitable for archiving to PDC. Created copy will be placed in\n"\
                                               "the same root path as the runfolder, with suffix '_archive'. If the destination\n"\
                                               "copy already exists then the script will abort.\n\n"\
                                               "The script will also scan for expected subdir/link 'Unaligned' in the runfolder\n"\
                                               "to archive. If it doesn't exist then it will abort. Inside 'Unaligned' it will\n"\
                                               "look for fastq.gz files. If the number of files found are less than the\n"\
                                               "specified threshold value then the script will abort.",
                                   formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("runfolder", help="path to the runfolder to archive")
  parser.add_argument("-e", "--exclude", action='append', help="filename to exclude from archive (argument can be repeated)")
  parser.add_argument("-t", "--threshold", default=10, type=int, help="will abort if less than this many FASTQ files are found (default 10)") 
  parser.add_argument("-r", "--remove", default='false', type=str2bool, help="if set to true then script will remove any already existing archive directories (default false)") 
  
  args = parser.parse_args()
  srcdir = os.path.abspath(args.runfolder)
  exclude = args.exclude
  threshold = args.threshold
  remove = args.remove

  destdir = srcdir + "_archive" 
  verify_src(srcdir, threshold)
  verify_dest(destdir, remove)
  create_dest(srcdir, destdir, exclude)
