#
#    Project: mxPluginExec
#             http://www.edna-site.org
#
#    Copyright (C) 2011-2013 European Synchrotron Radiation Facility
#                            Grenoble, France
#
#    Principal authors:      Olof Svensson (svensson@esrf.fr) 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    and the GNU Lesser General Public License  along with this program.  
#    If not, see <http://www.gnu.org/licenses/>.
#


__author__ = "Olof Svensson"
__contact__ = "svensson@esrf.fr"
__license__ = "LGPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20140623"

import os

from EDAssert import EDAssert
from EDTestCasePluginExecute import EDTestCasePluginExecute


class EDTestCasePluginExecuteMXWaitFilev1_1_bigFileTimeout(EDTestCasePluginExecute):

    def __init__(self, _strTestName=None):
        EDTestCasePluginExecute.__init__(self, "EDPluginMXWaitFilev1_1")
        self.setDataInputFile(os.path.join(self.getPluginTestsDataHome(), \
                                           "XSDataInputMXWaitFile_bigFileTimeout.xml"))
        self.setNoExpectedWarningMessages(1)
        
    def preProcess(self):
        EDTestCasePluginExecute.preProcess(self)
        self.loadTestImage([ "ref-testscale_1_0001.img" ])

    def testExecute(self):
        self.run()
        # Check timeout
        edPlugin = self.getPlugin()
        EDAssert.equal(True, edPlugin.dataOutput.timedOut.value, "TimedOut should be False")

    def process(self):
        self.addTestMethod(self.testExecute)


