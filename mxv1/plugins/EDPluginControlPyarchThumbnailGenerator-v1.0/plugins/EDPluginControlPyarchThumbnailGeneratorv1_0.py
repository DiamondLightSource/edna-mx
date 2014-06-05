#
#    Project: MXv1
#             http://www.edna-site.org
#
#    Copyright (C) 2010-2014 ESRF
#
#    Principal author:        Olof Svensson
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from EDFactoryPluginStatic import EDFactoryPluginStatic

__author__ = "Olof Svensson"
__license__ = "GPLv3+"
__copyright__ = "Copyrigth (c) 2010 ESRF"

import os, tempfile

from EDVerbose import EDVerbose
from EDPluginControl import EDPluginControl
from EDFactoryPluginStatic import EDFactoryPluginStatic

EDFactoryPluginStatic.loadModule("EDHandlerESRFPyarchv1_0")

from EDHandlerESRFPyarchv1_0 import EDHandlerESRFPyarchv1_0

from XSDataCommon import XSDataFile
from XSDataCommon import XSDataBoolean
from XSDataCommon import XSDataDouble
from XSDataCommon import XSDataDoubleWithUnit
from XSDataCommon import XSDataInteger
from XSDataCommon import XSDataString
from XSDataPyarchThumbnailGeneratorv1_0 import XSDataInputPyarchThumbnailGenerator
from XSDataPyarchThumbnailGeneratorv1_0 import XSDataResultPyarchThumbnailGenerator

EDFactoryPluginStatic.loadModule("XSDataExecThumbnail")
from XSDataExecThumbnail import XSDataInputExecThumbnail

EDFactoryPluginStatic.loadModule("EDPluginWaitFile")
from EDPluginWaitFile import EDPluginWaitFile
from XSDataWaitFilev1_0 import XSDataInputWaitFile


class EDPluginControlPyarchThumbnailGeneratorv1_0(EDPluginControl):
    """
    This control plugin uses EDPluginExecThumbnailv10 for creating two JPEG images from
    a diffraction image: one 1024x1024 (imagename.jpeg) and one 256x256 (imagename.thumb.jpeg).    
    """


    def __init__(self):
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputPyarchThumbnailGenerator)
        self.setDataOutput(XSDataResultPyarchThumbnailGenerator())
        self.strExecThumbnailPluginName = "EDPluginExecThumbnailv10"
        self.edPluginExecThumbnail = None
        self.strWaitFilePluginName = "EDPluginWaitFile"
        self.edPluginWaitFile = None
        self.strOutputPath = None
        self.strOutputPathWithoutExtension = None
        self.xsDataFilePathToThumbnail = None
        self.xsDataFilePathToThumbnail2 = None
        self.iExpectedSize = 1000000



    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginControlPyarchThumbnailGeneratorv1_0.checkParameters")
        self.checkMandatoryParameters(self.getDataInput(), "Data Input is None")
        self.checkMandatoryParameters(self.getDataInput().getDiffractionImage(), "No diffraction image file path")



    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        self.DEBUG("EDPluginControlPyarchThumbnailGeneratorv1_0.preProcess")
        # Check that the input image exists and is of the expected type
        strPathToDiffractionImage = self.getDataInput().getDiffractionImage().getPath().getValue()
        strImageFileNameExtension = os.path.splitext(strPathToDiffractionImage)[1]
        if not strImageFileNameExtension in [".img", ".marccd", ".mccd", ".cbf"]:
            self.error("Unknown image file name extension for pyarch thumbnail generator: %s" % strPathToDiffractionImage)
            self.setFailure()
        else:
            # Load the waitFile plugin
            xsDataInputWaitFile = XSDataInputWaitFile()
            xsDataInputWaitFile.setExpectedSize(XSDataInteger(self.iExpectedSize))
            xsDataInputWaitFile.setExpectedFile(self.getDataInput().getDiffractionImage())
            if self.getDataInput().getWaitForFileTimeOut():
                xsDataInputWaitFile.setTimeOut(self.getDataInput().getWaitForFileTimeOut())
            self.edPluginWaitFile = EDPluginWaitFile()
            self.edPluginWaitFile.setDataInput(xsDataInputWaitFile)
            # Load the execution plugin
            self.edPluginExecThumbnail = self.loadPlugin(self.strExecThumbnailPluginName)
            xsDataInputExecThumbnail = XSDataInputExecThumbnail()
            xsDataInputExecThumbnail.setInputImagePath(self.getDataInput().getDiffractionImage())
            xsDataInputExecThumbnail.setLevelsInvert(XSDataBoolean(True))
            xsDataInputExecThumbnail.setLevelsMin(XSDataDoubleWithUnit(0.0))
            xsDataDoubleWithUnitLevelsMax = XSDataDoubleWithUnit(99.95)
            xsDataDoubleWithUnitLevelsMax.setUnit(XSDataString("%"))
            xsDataInputExecThumbnail.setLevelsMax(xsDataDoubleWithUnitLevelsMax)
            xsDataInputExecThumbnail.setFilterDilatation([XSDataInteger(4)])
            xsDataInputExecThumbnail.setLevelsColorize(XSDataBoolean(False))
            xsDataInputExecThumbnail.setThumbHeight(XSDataInteger(1024))
            xsDataInputExecThumbnail.setThumbWidth(XSDataInteger(1024))
            xsDataInputExecThumbnail.setKeepRatio(XSDataBoolean(False))
            # Output path
            strImageNameWithoutExt = os.path.basename(os.path.splitext(strPathToDiffractionImage)[0])
            strImageDirname = os.path.dirname(strPathToDiffractionImage)
            if self.getDataInput().getForcedOutputDirectory():
                strForcedOutputDirectory = self.getDataInput().getForcedOutputDirectory().getPath().getValue()
                if not os.access(strForcedOutputDirectory, os.W_OK):
                    self.error("Cannot write to forced output directory : %s" % strForcedOutputDirectory)
                    self.setFailure()
                else:
                    self.strOutputPathWithoutExtension = os.path.join(strForcedOutputDirectory, strImageNameWithoutExt)
            else:
                # Try to store in the ESRF pyarch directory
                strOutputDirname = EDHandlerESRFPyarchv1_0.createPyarchFilePath(strImageDirname)
                # Check that output pyarch path exists and is writeable:
                bIsOk = False
                if strOutputDirname:
                    if not os.path.exists(strOutputDirname):
                        # Try to create the directory
                        try:
                            os.makedirs(strOutputDirname)
                            bIsOk = True
                        except BaseException, e:
                            self.WARNING("Couldn't create the directory %s" % strOutputDirname)
                    elif os.access(strOutputDirname, os.W_OK):
                        bIsOk = True
                if not bIsOk:
                    self.warning("Cannot write to pyarch directory: %s" % strOutputDirname)
                    strOutputDirname = tempfile.mkdtemp("", "EDPluginPyarchThumbnailv10_", "/tmp")
                    self.warning("Writing thumbnail images to: %s" % strOutputDirname)
                self.strOutputPathWithoutExtension = os.path.join(strOutputDirname, strImageNameWithoutExt)
            self.strOutputPath = os.path.join(self.strOutputPathWithoutExtension + ".jpeg")
            xsDataInputExecThumbnail.setOutputPath(XSDataFile(XSDataString(self.strOutputPath)))
            self.edPluginExecThumbnail.setDataInput(xsDataInputExecThumbnail)


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginControlPyarchThumbnailGeneratorv1_0.process")
        if self.edPluginExecThumbnail and self.edPluginWaitFile:
            self.edPluginWaitFile.connectSUCCESS(self.doSuccessWaitFile)
            self.edPluginWaitFile.connectFAILURE(self.doFailureWaitFile)
            self.edPluginWaitFile.executeSynchronous()



    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginControlPyarchThumbnailGeneratorv1_0.postProcess")
        # Create some output data
        xsDataResult = XSDataResultPyarchThumbnailGenerator()
        if self.xsDataFilePathToThumbnail:
            xsDataResult.setPathToJPEGImage(self.xsDataFilePathToThumbnail)
        if self.xsDataFilePathToThumbnail2:
            xsDataResult.setPathToThumbImage(self.xsDataFilePathToThumbnail2)
        self.setDataOutput(xsDataResult)


    def doSuccessWaitFile(self, _edPlugin=None):
        self.DEBUG("EDPluginControlID29CreateThumbnailv1_0.doSuccessWaitFile")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginControlID29CreateThumbnailv1_0.doSuccessWaitFile")
        # Check that the image is really there
        # The image is here - make the first thumbnail
        if not self.edPluginWaitFile.getDataOutput().getTimedOut().getValue():
            self.edPluginExecThumbnail.connectSUCCESS(self.doSuccessExecThumbnail)
            self.edPluginExecThumbnail.connectFAILURE(self.doFailureExecThumbnail)
            self.edPluginExecThumbnail.executeSynchronous()
        else:
            self.error("Time-out while waiting for image!")
            self.setFailure()


    def doFailureWaitFile(self, _edPlugin=None):
        self.DEBUG("EDPluginControlID29CreateThumbnailv1_0.doFailureWaitFile")
        self.retrieveFailureMessages(_edPlugin, "EDPluginControlID29CreateThumbnailv1_0.doFailureWaitFile")
        # To be removed if failure of the exec plugin shouldn't make the control plugin to fail:
        self.setFailure()


    def doSuccessExecThumbnail(self, _edPlugin=None):
        self.DEBUG("EDPluginControlPyarchThumbnailGeneratorv1_0.doSuccessExecThumbnail")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginControlPyarchThumbnailGeneratorv1_0.doSuccessExecThumbnail")
        # Retrieve the output path
        self.xsDataFilePathToThumbnail = self.edPluginExecThumbnail.getDataOutput().getThumbnailPath()
        # Run the plugin again, this time with the first thumbnail as input
        self.edPluginExecThumbnail2 = self.loadPlugin(self.strExecThumbnailPluginName)
        xsDataInputExecThumbnail = XSDataInputExecThumbnail()
        xsDataInputExecThumbnail.setInputImagePath(self.edPluginExecThumbnail.getDataOutput().getThumbnailPath())
        xsDataInputExecThumbnail.setThumbHeight(XSDataInteger(256))
        xsDataInputExecThumbnail.setThumbWidth(XSDataInteger(256))
        xsDataInputExecThumbnail.setKeepRatio(XSDataBoolean(False))
        xsDataInputExecThumbnail.setOutputPath(XSDataFile(XSDataString(self.strOutputPathWithoutExtension + ".thumb.jpeg")))
        self.edPluginExecThumbnail2.setDataInput(xsDataInputExecThumbnail)
        self.edPluginExecThumbnail2.connectSUCCESS(self.doSuccessExecThumbnail2)
        self.edPluginExecThumbnail2.connectFAILURE(self.doFailureExecThumbnail2)
        self.edPluginExecThumbnail2.executeSynchronous()



    def doFailureExecThumbnail(self, _edPlugin=None):
        self.DEBUG("EDPluginControlPyarchThumbnailGeneratorv1_0.doFailureExecThumbnail")
        self.retrieveFailureMessages(_edPlugin, "EDPluginControlPyarchThumbnailGeneratorv1_0.doFailureExecThumbnail")
        # To be removed if failure of the exec plugin shouldn't make the control plugin to fail:
        self.setFailure()


    def doSuccessExecThumbnail2(self, _edPlugin=None):
        self.DEBUG("EDPluginControlPyarchThumbnailGeneratorv1_0.doSuccessExecThumbnail2")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginControlPyarchThumbnailGeneratorv1_0.doSuccessExecThumbnail2")
        self.xsDataFilePathToThumbnail2 = self.edPluginExecThumbnail2.getDataOutput().getThumbnailPath()


    def doFailureExecThumbnail2(self, _edPlugin=None):
        self.DEBUG("EDPluginControlPyarchThumbnailGeneratorv1_0.doFailureExecThumbnail2")
        self.retrieveFailureMessages(_edPlugin, "EDPluginControlPyarchThumbnailGeneratorv1_0.doFailureExecThumbnail2")
        # To be removed if failure of the exec plugin shouldn't make the control plugin to fail:
        self.setFailure()

