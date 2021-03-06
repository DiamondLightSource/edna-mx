#
#    Project: EDNA MXv1
#             http://www.edna-site.org
#
#    File: "$Id: EDHandlerXSDataLabelitv10.py 769 2009-06-16 09:28:58Z svensson $"
#
#    Copyright (C) 2008-2009 European Synchrotron Radiation Facility
#                            Grenoble, France
#
#    Principal author:       Olof Svensson (svensson@esrf.fr)
#
#    Contributors:           Marie-Francoise Incardona (incardon@esrf.fr)
#                            Karl Levik (karl.levik@diamond.ac.uk)
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

from EDVerbose import EDVerbose
from EDUtilsSymmetry import EDUtilsSymmetry
from EDFactoryPluginStatic import EDFactoryPluginStatic

from XSDataCommon import XSDataString
from XSDataCommon import XSDataDouble
from XSDataCommon import XSDataInteger
from XSDataCommon import XSDataLength
from XSDataCommon import XSDataImage

from XSDataMXv1 import XSDataExperimentalCondition
from XSDataMXv1 import XSDataDetector
from XSDataMXv1 import XSDataIndexingResult
from XSDataMXv1 import XSDataCrystal
from XSDataMXv1 import XSDataIndexingSolution
from XSDataMXv1 import XSDataIndexingSolutionSelected
from XSDataMXv1 import XSDataStatisticsIndexing
from XSDataMXv1 import XSDataSpaceGroup
from XSDataMXv1 import XSDataOrientation


class EDHandlerXSDataPhenixv1_1:


    def generateXSDataInputLabelitIndexing(_xsDataIndexingInput):
        EDFactoryPluginStatic.loadModule("XSDataPhenixv1_1")
        from XSDataPhenixv1_1 import XSDataInputLabelitIndexing
        inputLabelitIndexing = XSDataInputLabelitIndexing()
        listXSDataImageReference = []
        dataCollection = _xsDataIndexingInput.dataCollection
        for subWedge in dataCollection.subWedge:
            for image in subWedge.image:
                inputLabelitIndexing.image.append(image.copy())

        xsDataCrystal = _xsDataIndexingInput.getCrystal()
        if xsDataCrystal is not None:
            xsDataSpaceGroup = xsDataCrystal.getSpaceGroup()
            if xsDataSpaceGroup is not None:
                xsDataStringName = xsDataSpaceGroup.getName()
                if xsDataStringName is not None:
                    inputLabelitIndexing.forcedSpaceGroup = xsDataStringName

        return inputLabelitIndexing
    generateXSDataInputLabelitIndexing = staticmethod(generateXSDataInputLabelitIndexing)


    def generateXSDataIndexingResult(_xsDataResultLabelitIndexing, _xsDataExperimentalCondition=None, _strSymopFileName=None):
        EDVerbose.DEBUG("EDHandlerXSDataLabelitv1_1.generateXSDataIndexingOutput")

        xsDataLabelitScreenOutput = _xsDataResultLabelitIndexing.screenOutput
        xsDataLabelitMosflmScriptsOutput = _xsDataResultLabelitIndexing.mosflmScriptsOutput

        iSelectedSolutionNumber = xsDataLabelitScreenOutput.getSelectedSolutionNumber().getValue()

        xsDataIndexingResult = XSDataIndexingResult()
        xsDataIndexingSolutionSelected = None

        for xsDataLabelitSolution in xsDataLabelitScreenOutput.getLabelitScreenSolution():
            xsDataCrystal = XSDataCrystal()
            xsDataSpaceGroup = XSDataSpaceGroup()
            edStringSpaceGroupName = EDUtilsSymmetry.getMinimumSymmetrySpaceGroupFromBravaisLattice(xsDataLabelitSolution.getBravaisLattice().getValue())
            xsDataSpaceGroup.setName(XSDataString(edStringSpaceGroupName))
            xsDataCrystal.setSpaceGroup(xsDataSpaceGroup)
            xsDataCrystal.setCell(xsDataLabelitSolution.getUnitCell())
            xsDataIndexingSolution = XSDataIndexingSolution()
            xsDataIndexingSolution.setCrystal(xsDataCrystal)
            iIndex = xsDataLabelitSolution.getSolutionNumber().getValue()
            xsDataIndexingSolution.setNumber(XSDataInteger(iIndex))
            xsDataIndexingResult.addSolution(xsDataIndexingSolution)
            if (iIndex == iSelectedSolutionNumber):
                xsDataIndexingSolutionSelected = XSDataIndexingSolutionSelected()
                xsDataIndexingSolutionSelected.setNumber(XSDataInteger(iIndex))
                edStringSelectedSpaceGroupName = edStringSpaceGroupName
                xsDataCellSelected = xsDataLabelitSolution.getUnitCell()
                fRmsdSelected = xsDataLabelitSolution.getRmsd().getValue()
                iNumberOfSpotsSelected = xsDataLabelitSolution.getNumberOfSpots().getValue()

        xsDataCrystalSelected = XSDataCrystal()
        xsDataSpaceGroupSelected = XSDataSpaceGroup()
        xsDataSpaceGroupSelected.setName(XSDataString(edStringSelectedSpaceGroupName))
        if not _strSymopFileName is None:
            xsDataSpaceGroupSelected.setITNumber(XSDataInteger(EDUtilsSymmetry.getITNumberFromSpaceGroupName(edStringSelectedSpaceGroupName, _strSymopFileName)))
        xsDataCrystalSelected.setSpaceGroup(xsDataSpaceGroupSelected)
        xsDataCrystalSelected.setCell(xsDataCellSelected)
        xsDataCrystalSelected.setMosaicity(XSDataDouble(xsDataLabelitScreenOutput.getMosaicity().getValue()))
        xsDataIndexingSolutionSelected.setCrystal(xsDataCrystalSelected)

        xsDataOrientation = XSDataOrientation()
        xsDataOrientation.setMatrixA(xsDataLabelitMosflmScriptsOutput.getAMatrix())
        xsDataOrientation.setMatrixU(xsDataLabelitMosflmScriptsOutput.getUMatrix())
        xsDataIndexingSolutionSelected.setOrientation(xsDataOrientation)

        xsDataStatisticsIndexing = XSDataStatisticsIndexing()

        if (_xsDataExperimentalCondition is not None):
            fBeamPositionXOrig = _xsDataExperimentalCondition.getDetector().getBeamPositionX().getValue()
            fBeamPositionYOrig = _xsDataExperimentalCondition.getDetector().getBeamPositionY().getValue()
            fBeamPositionXNew = xsDataLabelitScreenOutput.getBeamCentreX().getValue()
            fBeamPositionYNew = xsDataLabelitScreenOutput.getBeamCentreY().getValue()
            xsDataStatisticsIndexing.setBeamPositionShiftX(XSDataLength(fBeamPositionXOrig - fBeamPositionXNew))
            xsDataStatisticsIndexing.setBeamPositionShiftY(XSDataLength(fBeamPositionYOrig - fBeamPositionYNew))

        # xsDataStatisticsIndexing.setSpotDeviXSDataLength( dDistanceRefinedationAngular( XSDataAngle( dDeviationAngular ) )
        xsDataStatisticsIndexing.setSpotDeviationPositional(XSDataLength(fRmsdSelected))
        xsDataStatisticsIndexing.setSpotsUsed(XSDataInteger(iNumberOfSpotsSelected))
        xsDataStatisticsIndexing.setSpotsTotal(XSDataInteger(iNumberOfSpotsSelected))
        xsDataIndexingSolutionSelected.setStatistics(xsDataStatisticsIndexing)

        xsDataExperimentalConditionRefined = None
        if (_xsDataExperimentalCondition is None):
            xsDataExperimentalConditionRefined = XSDataExperimentalCondition()
        else:
            # Copy the incoming experimental condition
            xmlExperimentalCondition = _xsDataExperimentalCondition.marshal()
            xsDataExperimentalConditionRefined = XSDataExperimentalCondition.parseString(xmlExperimentalCondition)

        xsDataDetector = xsDataExperimentalConditionRefined.getDetector()
        if (xsDataDetector is None):
            xsDataDetector = XSDataDetector()

        xsDataDetector.setBeamPositionX(xsDataLabelitScreenOutput.getBeamCentreX())
        xsDataDetector.setBeamPositionY(xsDataLabelitScreenOutput.getBeamCentreY())
        xsDataDetector.setDistance(xsDataLabelitScreenOutput.getDistance())

        xsDataExperimentalConditionRefined.setDetector(xsDataDetector)
        xsDataIndexingSolutionSelected.setExperimentalConditionRefined(xsDataExperimentalConditionRefined)

        xsDataIndexingResult.setSelectedSolution(xsDataIndexingSolutionSelected)

        xsDataIndexingResult.setIndexingLogFile(xsDataLabelitScreenOutput.getPathToLogFile())

        return xsDataIndexingResult
    generateXSDataIndexingResult = staticmethod(generateXSDataIndexingResult)
