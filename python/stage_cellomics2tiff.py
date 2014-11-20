#!/usr/bin/python
import datetime
import glob
import logging
import math
from optparse import OptionParser
import os
import string
import subprocess
import sys
import time
import traceback

from mp_cellomics2tiff import CellomicsConverter
from utils import CellomicsUtils

logger = None

DRY_RUN = False

# input directory
INPUT_ROOT = None

# staging directory on compute server
STAGING_ROOT = None

# output root directory on lmu-active
OUTPUT_ROOT = None

CONVERSION_POSTFIX = "_tiff"

cutils = CellomicsUtils()

def is_converted(dataset):
    # list of converted datasets, in subfolders by user
    logger.debug("searching conversions: " + OUTPUT_ROOT + "/*/*")
    converted = glob.glob(OUTPUT_ROOT + "/*/*")
    for c in converted:
        # check if the folder name matches
        if string.find(c,dataset + CONVERSION_POSTFIX) != -1 and os.path.isdir(c):
            logger.debug("found existing conversion: " + c) 
            # return true if the folder has been converted already
            if cutils.isDatasetConverted(dir_in,c):
                #print "stage_cellomics2tiff:","CURRENT", dataset + CONVERSION_POSTFIX
                #print "stage_cellomics2tiff:","CONVERTED",c
                logger.debug("existing conversion is up to date, skipping...")
                return True
            else:
                logger.debug("existing conversion is not complete or up to date.")
                return False

def _run_and_log(cmd,msg):
    start = time.time()
    logger.info(msg)
    logger.info(cmd)
    if not DRY_RUN:
        os.system(cmd)
    logger.info("Completed in " + str(time.time()-start) + "s.")

def archive(dir_in, archive):
    dir_in = os.path.join(INPUT_ROOT, dir_in)
    msg = "Archiving " + dir_in + " to " + archive 
    cmd = "rsync -av --remove-source-files " + dir_in + " " + archive + "/"
    if DRY_RUN:
        cmd = "rsync -avn --remove-source-files " + dir_in + " " + archive + "/"
    _run_and_log(cmd,msg)

def stageAndConvert(dir_in):
    logger.debug(INPUT_ROOT + " " + dir_in)
    dir_in = os.path.join(INPUT_ROOT,dir_in)
    logger.info("dir_in:" + dir_in)

    # skip items that are not directories
    if not os.path.isdir(dir_in):
        return

    # skip of not a Cellomics dataset
    if not cutils.isCellomicsDataset(dir_in):
        logger.info("not a C01 dataset:" + dir_in)
        return
    
    head,dataset = os.path.split(dir_in)
    if is_converted(dataset):
        return


    staging_in = os.path.join(STAGING_ROOT,dataset)
    staging_out = staging_in + CONVERSION_POSTFIX

    # Create staging directories
    if not os.path.isdir(staging_in):
        os.makedirs(staging_in)
    if not os.path.isdir(staging_out):
        os.makedirs(staging_out)

    start_time = time.time()

    # Copy data to the cluster
    msg ="copying (rsync) data to " + staging_in + "..."
    cmd = "rsync -rt " + dir_in + "/ " + staging_in
    _run_and_log(cmd,msg)

    # Convert the data
    start_time_convert = time.time()
    logger.info("converting...")
    creator = "creator"
    
    if not DRY_RUN:
        converter = CellomicsConverter()
        converter.convert(staging_in,staging_out)
        logger.info("Time elapsed: " + str(time.time() - start_time_convert) + "s")

        # find the creator of the data from metadata
        csv = os.path.join(staging_out,"metadata","asnPlate.csv")
        creator = cutils.findCreator(csv)
        
    # Copy results outside the cluster
    dir_out = os.path.join(OUTPUT_ROOT,creator)
    if not os.path.isdir(dir_out):
        os.makedirs(dir_out)
    msg = "copying " + staging_out + " to " + dir_out
    cmd = "rsync -r " + staging_out + " " + dir_out
    _run_and_log(cmd,msg)

    # Remove data from staging area
    msg = "cleaning up staging area"
    cmd = "rm -rf " + staging_in + " " + staging_out
    _run_and_log(cmd,msg)

    logger.info("Total time elapsed: " + str(time.time() - start_time) + "s")

 
##
## Main part
##
if __name__=='__main__':

    usage = """%prog [options] input_dir staging_dir output_dir

                Stage and convert CellInsight data to TIF.
                RUN '%prog -h for options.'"""

    parser = OptionParser(usage=usage)
    parser.add_option('-n', '--dryrun', action="store_true", \
                      default=False, help="Print actions but do not execute.")
    parser.add_option('-i', '--input', default='/input', help="Input directory [default: %default].")
    parser.add_option('-s', '--staging', default='/tmp', help="Staging directory [default: %default].")
    parser.add_option('-o', '--output', default='/output', help="Output directory [default: %default].")
    parser.add_option('-a', '--archive', help="Archive directory: check if datasets in -i have been converted to -o, if yes, move -i to archive.")
    parser.add_option('-d','--debug', action="store_true", help="Set log level to DEBUG.")

    opts,args = parser.parse_args()
     
    INPUT_ROOT = opts.input
    STAGING_ROOT = opts.staging
    OUTPUT_ROOT = opts.output

    ARCHIVE_ROOT = None
    if opts.archive:
        ARCHIVE_ROOT = opts.archive
 
    # log directory
    if opts.archive:
        logdir = os.path.join(ARCHIVE_ROOT, "log")
    else:
        logdir = os.path.join(OUTPUT_ROOT, "log")
    if not os.path.isdir(logdir):
        os.makedirs(logdir)

    # log file
    t = time.time()
    ft = datetime.datetime.fromtimestamp(t).strftime('%Y%m%d-%H%M%S')
    logfile = os.path.join(logdir,'sta_cellomics2tiff_%s.log'%(ft))

    # logger
    loglevel = logging.INFO
    if opts.debug:
        loglevel = logging.DEBUG
    logformat = '[%(pathname)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s'
    logging.basicConfig(filename=logfile,level=loglevel,format=logformat)
    logger = logging.getLogger(__name__)


    if opts.dryrun:
        logger.info("DRY RUN")
        DRY_RUN = True

    logger.info("INPUT_ROOT: " + INPUT_ROOT)
    logger.info("OUTPUT_ROOT: " + OUTPUT_ROOT)
    logger.info("ARCHIVE_ROOT: " + str(ARCHIVE_ROOT))

    # lock file
    pidfile_name = os.path.join(OUTPUT_ROOT, "stage_cellomics2tiff.pid")

    # check if conversion is already running
    if os.path.isfile(pidfile_name):
        logger.info("Conversion is already running, exiting...")
        sys.exit(0)

    # write process id to lock file
    pidfile = open(pidfile_name,'w')
    pid = os.getpid()
    print >> pidfile, str(pid)
    pidfile.close()

    # process all CellInsight datasets in the input directory
    datasets = []
    try:
        datasets = os.listdir(INPUT_ROOT)
    except Exception as e:
        logger.exception("Failed to read input directory.")
    
    logger.info("datasets:" + str(datasets))

    for dir_in in datasets:
        try:
            if ARCHIVE_ROOT:
                archive(dir_in,ARCHIVE_ROOT)
            else:
                stageAndConvert(dir_in)
        except Exception as e:
            logger.exception("Failed to convert (or archive) " + dir_in)

    # remove lock file
    os.remove(pidfile_name)

    logger.info("Done.")

