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
__date__ = "20140704"
__status__ = "production"

import os, datetime

from EDPluginExec import EDPluginExec
from EDFactoryPluginStatic import EDFactoryPluginStatic

EDFactoryPluginStatic.loadModule("EDInstallJurkoSuds94664ddd46a6")
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from suds.sax.date import DateTime

from XSDataCommon import XSDataString

from XSDataISPyBv1_4 import XSDataInputISPyBGetPdbFilePath
from XSDataISPyBv1_4 import XSDataResultISPyBGetPdbFilePath


class EDPluginISPyBGetPdbFilePathv1_4(EDPluginExec):
    """
    Plugin for rertrieving path to pdb file
    """

    def __init__(self):
        EDPluginExec.__init__(self)
        self.setXSDataInputClass(XSDataInputISPyBGetPdbFilePath)
        self.strUserName = None
        self.strPassWord = None
        self.strToolsForCollectionWebServiceWsdl = None
        self.dataCollectionId = None
        self.strPathToPdbFile = None


    def configure(self):
        """
        Gets the web servise wdsl parameters from the config file and stores them in class member attributes.
        """
        EDPluginExec.configure(self)
        self.strUserName = str(self.config.get("userName"))
        if self.strUserName is None:
            self.ERROR("EDPluginISPyBGetPdbFilePathv1_4.configure: No user name found in configuration!")
            self.setFailure()
        self.strPassWord = str(self.config.get("passWord"))
        if self.strPassWord is None:
            self.ERROR("EDPluginISPyBGetPdbFilePathv1_4.configure: No pass word found in configuration!")
            self.setFailure()
        self.strToolsForCollectionWebServiceWsdl = self.config.get("toolsForCollectionWebServiceWsdl")
        if self.strToolsForCollectionWebServiceWsdl is None:
            self.ERROR("EDPluginISPyBGetPdbFilePathv1_4.configure: No toolsForCollectionWebServiceWsdl found in configuration!")
            self.setFailure()

    def getXSValue(self, _xsData, _oDefaultValue=None, _iMaxStringLength=255):
        if _xsData is None:
            oReturnValue = _oDefaultValue
        else:
            oReturnValue = _xsData.value
        if type(oReturnValue) == bool:
            if oReturnValue:
                oReturnValue = "1"
            else:
                oReturnValue = "0"
        elif (type(oReturnValue) == str) or (type(oReturnValue) == unicode):
            if len(oReturnValue) > _iMaxStringLength:
                strOldString = oReturnValue
                oReturnValue = oReturnValue[0:_iMaxStringLength - 3] + "..."
                self.warning("String truncated to %d characters for ISPyB! Original string: %s" % (_iMaxStringLength, strOldString))
                self.warning("Truncated string: %s" % oReturnValue)
        return oReturnValue



    def process(self, _edObject=None):
        """
        Uses ToolsForCollectionWebService 
        """
        EDPluginExec.process(self)
        self.DEBUG("EDPluginISPyBGetPdbFilePathv1_4.process")
        httpAuthenticatedToolsForCollectionWebService = HttpAuthenticated(username=self.strUserName, password=self.strPassWord)
        clientToolsForCollectionWebService = Client(self.strToolsForCollectionWebServiceWsdl, transport=httpAuthenticatedToolsForCollectionWebService)
        # Loop over all positions
        xsDataInputISPyBGetPdbFilePath = self.getDataInput()
        iDataCollectionId = self.getXSValue(xsDataInputISPyBGetPdbFilePath.dataCollectionId)
        self.strPathToPdbFile = clientToolsForCollectionWebService.service.getPdbFilePath(
                                    iDataCollectionId, \
                                    )
        self.DEBUG("EDPluginISPyBGetPdbFilePathv1_4.process: path to pdb file=%r" % self.strPathToPdbFile)





    def finallyProcess(self, _edObject=None):
        EDPluginExec.finallyProcess(self)
        self.DEBUG("EDPluginISPyBGetPdbFilePathv1_4.finallyProcess")
        xsDataResultISPyBGetPdbFilePath = XSDataResultISPyBGetPdbFilePath()
        if self.strPathToPdbFile is not None:
            xsDataResultISPyBGetPdbFilePath.pdbFilePath = XSDataString(self.strPathToPdbFile)
        self.setDataOutput(xsDataResultISPyBGetPdbFilePath)

