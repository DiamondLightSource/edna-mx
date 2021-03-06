#
#    Project: PROJECT
#             http://www.edna-site.org
#
#    File: "$Id$"
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

import os

from EDVerbose                           import EDVerbose
from EDAssert                            import EDAssert
from EDTestCasePluginExecute             import EDTestCasePluginExecute

class EDTestCasePluginExecuteControlCharacterisationv1_4(EDTestCasePluginExecute):


    def __init__(self, _strTestName=None):
        EDTestCasePluginExecute.__init__(self, "EDPluginControlCharacterisationv1_4")
        self.setRequiredPluginConfiguration("EDPluginMOSFLMIndexingv10")
        self.setRequiredPluginConfiguration("EDPluginMOSFLMIntegrationv10")
        self.setRequiredPluginConfiguration("EDPluginMOSFLMGeneratePredictionv10")
        self.setRequiredPluginConfiguration("EDPluginLabelitIndexingv1_1")
        self.setRequiredPluginConfiguration("EDPluginDistlSignalStrengthv1_1")
        self.setRequiredPluginConfiguration("EDPluginBestv1_2")
        self.setRequiredPluginConfiguration("EDPluginRaddosev10")
        self.setDataInputFile(os.path.join(self.getPluginTestsDataHome(), \
                                           "XSDataInputCharacterisation_reference.xml"))
        self.setReferenceDataOutputFile(os.path.join(self.getPluginTestsDataHome(), \
                                                     "XSDataResultCharacterisation_reference.xml"))


    def preProcess(self):
        EDTestCasePluginExecute.preProcess(self)
        self.loadTestImage([ "ref-testscale_1_001.img", "ref-testscale_1_002.img" ])




    def testExecute(self):
        self.run()



    def process(self):
        self.addTestMethod(self.testExecute)


