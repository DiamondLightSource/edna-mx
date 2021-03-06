# coding: utf8
#
#    Project: MX Plugin Exec
#             http://www.edna-site.org
#
#    Copyright (C) ESRF
#
#    Principal author:       Olof Svensson
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

__author__ = "Olof Svensson"
__license__ = "GPLv3+"
__copyright__ = "ESRF"

import os, time, shlex

from EDPluginExecProcessScript import EDPluginExecProcessScript
from EDUtilsTable              import EDUtilsTable
from EDFactoryPluginStatic import EDFactoryPluginStatic
from EDUtilsFile import EDUtilsFile

EDFactoryPluginStatic.loadModule("markupv1_10")
import markupv1_10

from XSDataCommon import XSDataDouble
from XSDataCommon import XSDataString
from XSDataCommon import XSDataFile
from XSDataCommon import XSDataAngle

from XSDataDnaTables import dna_tables

from XSDataCommon import XSDataInteger
from XSDataCommon import XSDataDouble
from XSDataCommon import XSDataString

from XSDataDozorv1_0 import XSDataInputDozor
from XSDataDozorv1_0 import XSDataResultDozor
from XSDataDozorv1_0 import XSDataImageDozor

class EDPluginDozorv1_0(EDPluginExecProcessScript):
    """
    This plugin runs the Dozor program written by Sasha Popov
    """


    def __init__(self):
        EDPluginExecProcessScript.__init__(self)
        self.setXSDataInputClass(XSDataInputDozor)
        self.setDataOutput(XSDataResultDozor())
        self.strImageLinkSubDirectory = "img"
        self.defaultFractionPolarization = 0.99
        self.defaultImageStep = 1
        self.startingAngle = 0.0
        self.firstImageNumber = None
        self.oscillationRange = None
        self.overlap = 0.0
        self.ixMin = None
        self.iyMin = None
        self.ixMax = None
        self.iyMax = None
        # Default values for ESRF Pilatus6M
        self.ixMinPilatus6m = 1
        self.ixMaxPilatus6m = 1270
        self.iyMinPilatus6m = 1190
        self.iyMaxPilatus6m = 1310
        # Default values for ESRF Pilatus2M
        self.ixMinPilatus2m = 1
        self.ixMaxPilatus2m = 840
        self.iyMinPilatus2m = 776
        self.iyMaxPilatus2m = 852
        # Default values for ESRF Eiger4M
        self.ixMinEiger4m = 1
        self.ixMaxEiger4m = 840
        self.iyMinEiger4m = 776
        self.iyMaxEiger4m = 852
        # Bad zones
        self.strBad_zona = None

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginDozorv1_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")


    def preProcess(self, _edObject=None):
        EDPluginExecProcessScript.preProcess(self)
        self.DEBUG("EDPluginDozorv1_0.preProcess")
        xsDataInputDozor = self.getDataInput()
        # First image number and osc range for output angle calculations
        self.firstImageNumber = xsDataInputDozor.firstImageNumber.value
        self.oscillationRange = xsDataInputDozor.oscillationRange.value
        if xsDataInputDozor.overlap is not None:
            self.overlap = xsDataInputDozor.overlap.value
        # Retrieve config (if any)
        self.ixMin = self.config.get("ixMin")
        self.ixMax = self.config.get("ixMax")
        self.iyMin = self.config.get("iyMin")
        self.iyMax = self.config.get("iyMax")
        # Eventual bad zones
        self.strBad_zona = self.config.get("bad_zona")
        if xsDataInputDozor.radiationDamage is not None and xsDataInputDozor.radiationDamage.value:
            self.setScriptCommandline("-rd dozor.dat")
        else:
            self.setScriptCommandline("-p dozor.dat")
        strCommands = self.generateCommands(xsDataInputDozor)
        EDUtilsFile.writeFile(os.path.join(self.getWorkingDirectory(), "dozor.dat"), strCommands)


    def postProcess(self, _edObject=None):
        EDPluginExecProcessScript.postProcess(self)
        self.DEBUG("EDPluginDozorv1_0.postProcess")
        self.dataOutput = self.parseOutput(os.path.join(self.getWorkingDirectory(),
                                                        self.getScriptLogFileName()))



    def generateCommands(self, _xsDataInputDozor):
        """
        This method creates the input file for dozor
        """
        self.DEBUG("EDPluginDozorv1_0.generateCommands")
        strCommandText = None
        if self.ixMin is None or self.ixMax is None or self.iyMin is None or self.iyMax is None:
            # One configuration value is missing - use default values
            if _xsDataInputDozor.detectorType.value == "pilatus2m":
                self.ixMin = self.ixMinPilatus2m
                self.ixMax = self.ixMaxPilatus2m
                self.iyMin = self.iyMinPilatus2m
                self.iyMax = self.iyMaxPilatus2m
            elif _xsDataInputDozor.detectorType.value == "pilatus6m":
                self.ixMin = self.ixMinPilatus6m
                self.ixMax = self.ixMaxPilatus6m
                self.iyMin = self.iyMinPilatus6m
                self.iyMax = self.iyMaxPilatus6m
            elif _xsDataInputDozor.detectorType.value == "eiger4m":
                self.ixMin = self.ixMinEiger4m
                self.ixMax = self.ixMaxEiger4m
                self.iyMin = self.iyMinEiger4m
                self.iyMax = self.iyMaxEiger4m
        if _xsDataInputDozor is not None:
            self.setProcessInfo("name template: %s, first image no: %d, no images: %d" % (
                _xsDataInputDozor.nameTemplateImage.value,
                _xsDataInputDozor.firstImageNumber.value,
                _xsDataInputDozor.numberImages.value))
            strCommandText = "!\n"
            strCommandText += "detector %s\n" % _xsDataInputDozor.detectorType.value
            strCommandText += "exposure %.3f\n" % _xsDataInputDozor.exposureTime.value
            strCommandText += "spot_size %d\n" % _xsDataInputDozor.spotSize.value
            strCommandText += "detector_distance %.3f\n" % _xsDataInputDozor.detectorDistance.value
            strCommandText += "X-ray_wavelength %.3f\n" % _xsDataInputDozor.wavelength.value
            if _xsDataInputDozor.fractionPolarization is None:
                fractionPolarization = self.defaultFractionPolarization
            else:
                fractionPolarization = _xsDataInputDozor.fractionPolarization.value
            strCommandText += "fraction_polarization %.3f\n" % fractionPolarization
            strCommandText += "pixel_min 0\n"
            strCommandText += "pixel_max 64000\n"
            if self.ixMin is not None:
                strCommandText += "ix_min %d\n" % self.ixMin
                strCommandText += "ix_max %d\n" % self.ixMax
                strCommandText += "iy_min %d\n" % self.iyMin
                strCommandText += "iy_max %d\n" % self.iyMax
            if self.strBad_zona is not None:
                strCommandText += "bad_zona %s\n" % self.strBad_zona
            strCommandText += "orgx %.1f\n" % _xsDataInputDozor.orgx.value
            strCommandText += "orgy %.1f\n" % _xsDataInputDozor.orgy.value
            strCommandText += "oscillation_range %.3f\n" % _xsDataInputDozor.oscillationRange.value
            if _xsDataInputDozor.imageStep is None:
                imageStep = self.defaultImageStep
            else:
                imageStep = _xsDataInputDozor.imageStep.value
            strCommandText += "image_step %.3f\n" % imageStep
            if _xsDataInputDozor.startingAngle is None:
                self.startingAngle = self.defaultStartingAngle
            else:
                self.startingAngle = _xsDataInputDozor.startingAngle.value
            strCommandText += "starting_angle %.3f\n" % self.startingAngle
            strCommandText += "first_image_number %d\n" % _xsDataInputDozor.firstImageNumber.value
            strCommandText += "number_images %d\n" % _xsDataInputDozor.numberImages.value
            if _xsDataInputDozor.wedgeNumber is not None:
                strCommandText += "wedge_number %d\n" % _xsDataInputDozor.wedgeNumber.value
            strCommandText += "name_template_image %s\n" % _xsDataInputDozor.nameTemplateImage.value
            strCommandText += "end\n"
        return strCommandText


    def parseOutput(self, _strFileName):
        """
        This method parses the output of dozor
        """
        xsDataResultDozor = XSDataResultDozor()
        strOutput = EDUtilsFile.readFile(_strFileName)
        # Skip the four first lines
        listOutput = strOutput.split("\n")[6:]

        for strLine in listOutput:
            # Remove "|"
            listLine = shlex.split(strLine.replace("|", " "))
#            print listLine
            if listLine != [] and not strLine.startswith("-") and not strLine.startswith("h"):
                xsDataImageDozor = XSDataImageDozor()
                imageNumber = int(listLine[0])
                angle = self.startingAngle + (imageNumber - self.firstImageNumber) * (self.oscillationRange - self.overlap) + self.oscillationRange / 2.0
                xsDataImageDozor.number = XSDataInteger(imageNumber)
                xsDataImageDozor.angle = XSDataAngle(angle)
                if listLine[4].startswith("-"):
                    xsDataImageDozor.spotsNumOf = XSDataInteger(listLine[1])
                    xsDataImageDozor.spotsIntAver = self.parseDouble(listLine[2])
                    xsDataImageDozor.spotsResolution = self.parseDouble(listLine[3])
                    xsDataImageDozor.mainScore = self.parseDouble(listLine[7])
                    xsDataImageDozor.spotScore = self.parseDouble(listLine[8])
                    xsDataImageDozor.visibleResolution = self.parseDouble(listLine[9])
                else:
                    xsDataImageDozor.spotsNumOf = XSDataInteger(listLine[1])
                    xsDataImageDozor.spotsIntAver = self.parseDouble(listLine[2])
                    xsDataImageDozor.spotsResolution = self.parseDouble(listLine[3])
                    xsDataImageDozor.powderWilsonScale = self.parseDouble(listLine[4])
                    xsDataImageDozor.powderWilsonBfactor = self.parseDouble(listLine[5])
                    xsDataImageDozor.powderWilsonResolution = self.parseDouble(listLine[6])
                    xsDataImageDozor.powderWilsonCorrelation = self.parseDouble(listLine[7])
                    xsDataImageDozor.powderWilsonRfactor = self.parseDouble(listLine[8])
                    xsDataImageDozor.mainScore = self.parseDouble(listLine[9])
                    xsDataImageDozor.spotScore = self.parseDouble(listLine[10])
                    xsDataImageDozor.visibleResolution = self.parseDouble(listLine[11])
                # Dozor spot file
                strWorkingDir = self.getWorkingDirectory()
                if strWorkingDir is not None:
                    strSpotFile = os.path.join(self.getWorkingDirectory(), "%05d.spot" % xsDataImageDozor.number.value)
                    if os.path.exists(strSpotFile):
                        xsDataImageDozor.spotFile = XSDataFile(XSDataString(strSpotFile))
#                print xsDataImageDozor.marshal()
                xsDataResultDozor.addImageDozor(xsDataImageDozor)
            elif strLine.startswith("h"):
                xsDataResultDozor.halfDoseTime = XSDataDouble(strLine.split("=")[1].split()[0])
        return xsDataResultDozor

    def parseDouble(self, _strValue):
        returnValue = None
        try:
            returnValue = XSDataDouble(_strValue)
        except Exception as ex:
            self.warning("Error when trying to parse '" + _strValue + "': %r" % ex)
        return returnValue
