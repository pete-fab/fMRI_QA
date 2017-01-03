#!/usr/bin/env python
import argparse
from netdicom import AE, StorageSOPClass, VerificationSOPClass
import netdicom
from dicom.dataset import Dataset, FileDataset
from dicom import UID
#import dicom
#import tempfile
import my_logger as l
import directory
import config
import logging
from time import sleep
# netdicom.debug(True)


al = l.AllLogger()
rl = l.RuntimeLogger()


class DicomServer(AE):
    # callbacks
    def OnAssociateRequest(self, association):
        rl.info('association requested')


    def OnAssociateResponse(self, association):
        rl.info('Association response received')


    def OnReceiveEcho(self):
        rl.info('Echo received')


    def OnReceiveStore(self, SOPClass, DS):
        # sleep(0.1)
        rl.info('Received C-STORE')
        # do something with dataset. For instance, store it on disk.
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = DS.SOPClassUID
        file_meta.MediaStorageSOPInstanceUID = UID.generate_uid() #DS.SOPInstanceUID  # !! Need valid UID here
        file_meta.ImplementationClassUID = UID.pydicom_root_UID #"1.2.3.4"  # !!! Need valid UIDs here
        file_path = directory.joinPath([self.StorePath, str(DS.get('SeriesDate')), str(DS.get('SeriesDescription'))])
        directory.createPath(file_path)
        filename = directory.joinPath([file_path, "I%05d" % DS.get('InstanceNumber') + '.'+config.DATA_EXT])
        ds = FileDataset(filename, {}, file_meta=file_meta, preamble="\0" * 128)
        ds.update(DS)
        ds.is_little_endian = True
        ds.is_implicit_VR = True
        # print ds - prints all DICOM tags contained in the file prior its saving
        ds.save_as(filename)
        rl.info('File %s written' % filename)
        # must return appropriate status
        return SOPClass.Success

    def __init__(self):
        AE.__init__(self,config.DICOMSERVER_AET, config.DICOMSERVER_PORT, [], [StorageSOPClass, VerificationSOPClass])
        self.StorePath = config.DICOMSERVER_DIR

        # start AE
        rl.info('DICOM server starting ...')
        self.start()
        rl.info('DICOM server started')
        self.QuitOnKeyboardInterrupt()

if __name__ == "__main__":
    dcmSrv = DicomServer()