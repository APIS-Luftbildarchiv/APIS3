# -*- coding: utf-8 -*

import os, sys, subprocess
from PyQt5.QtWidgets import QMessageBox

class Image2Xmp():
    '''
    Image2Exif(metadataDict, imagePath)
    on instantiation this class updates the meta data of imagePath with info from metadataDict
    metadata will be written as 'Xmp.apis.metadata_key'
    '''

    def __init__(self, metadataDict, imagePath):

        self.metadataDict = metadataDict
        self.imagePath = imagePath

        if not os.path.isfile(self.imagePath):
            raise IOError('Was not able to read file {0}'.format(self.imagePath))

        #try:
        self.update_metaData()
        #except:
        #    raise IOError('Was not able to set metadata for {0}'.format(self.imagePath))


    def update_metaData(self):
        #try:
        commandItemTemplate = '-M"set Xmp.apis.{0} {1}"'
        command = 'exiv2 mo -M"reg apis /" {0} {1}'.format(" ".join([commandItemTemplate.format(k, str(v)) for k, v in self.metadataDict.items()]), self.imagePath)

        DETACHED_PROCESS = 0x00000008
        subprocess.run(command, creationflags=DETACHED_PROCESS)
        #QMessageBox.information(None, "XMP Command", "{}".format(command))

        #except Exception as e:
        #    print("> Error metadata", e)
        #    exc_type, exc_obj, exc_tb = sys.exc_info()
        #    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #   print(exc_type, fname, exc_tb.tb_lineno)