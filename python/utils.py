import glob
import os
import logging
import re

logger = logging.getLogger(__name__)

class CellomicsUtils:
    def findCreator(self,asnPlate):
        UNKNOWN = "UnknownCreator"
        creator = UNKNOWN

        # key to look for in csv
        KEY_CREATOR = "Creator"

        csv = open(asnPlate,'r')
        keys = csv.readline().split(',')
        values = csv.readline().split(',')
        csv.close()

        for i in range(1,len(keys)):
            # check that the value field exists,
            # it may be missing because of metadata error
            if keys[i] == KEY_CREATOR and len(values) > i:
                creator = values[i].replace('"','')

        if creator == UNKNOWN:
            logger.error("CellomicsUtils:findCreator: creator not found in ", asnPlate)

        return creator

    def getTifPath(self,C01,outputDir):
        head,tail = os.path.split(C01)
        tif = os.path.join(outputDir,tail.replace(".C01",".tif"))
        #print "C01:",C01
        #print "TIF:",tif
        return tif

    def isCellomicsDataset(self,inputDir):
        C01s = glob.glob(inputDir + "/*.C01")
        return len(C01s) != 0
        
    def isDatasetConverted(self,inputDir,outputDir):
        C01s = glob.glob(inputDir + "/*.C01")

        for C01 in C01s:
            tif = self.getTifPath(C01,outputDir)

            # if a tif file is missing, conversion is not complete
            if not os.path.isfile(tif):
                logger.debug("C01:" + C01)
                logger.debug("TIF:" + tif)
                logger.info("TIF file is missing: " + tif)
                return False
            # if the tif file exists but is older than C01,
            # conversion is not up to date
            else:
                otime = os.stat(C01).st_mtime
                ctime = os.stat(tif).st_mtime
                if otime > ctime:
                    logger.debug("C01:" + C01)
                    logger.debug("TIF:" + tif)
                    logger.debug("otime" + str(otime))
                    logger.debug("ctime" + str(ctime))
                    logger.info("TIF file is out of date: " + tif)
                    return False

        return True


if __name__=='__main__':

    c = CellomicsUtils()
    print c.findCreator('/mnt/lmu-active/LMU-active2/users/FROM_CSC_LMU/CellInsight/LMU-CELLINSIGHT_140625100001_converted/metadata/asnPlate.csv')

    dataset = 'LMU-CELLINSIGHT_140625100001'
    dataset = 'LMU-CELLINSIGHT_140210110003'
    base = '/mnt/lmu-active/LMU-active2/users'
    orig = base + '/FROM_CELLINSIGHT/' + dataset
    conv = base + '/FROM_CSC_LMU/CellInsight' + dataset + '_converted'
    c.isDatasetConverted(orig,conv)
    
