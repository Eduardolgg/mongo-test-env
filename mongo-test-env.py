#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# mongo-test-env.py
#
# Copyright (C) 2016  Eduardo L. García Glez <eduardo.l.g.g@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import socket
import pymongo
from pymongo import MongoClient

serverPortCounter = None
configServersString = ""

parameters = [
        { "name" : "Cluster Size", "option": "--tClusterSize", "value": 2 },
        { "name": "Replica Set Size", "option": "--tReplicaSetSize", "value": 3 },
        { "name": "Arviters", "option": "--tArviters", "value": 0 },
        { "name": "Shards Routers", "option": "--tRouters", "value": 1 },
	{ "name": "Config Servers", "option": "--tConfigServers", "value": 3},
	{ "name": "Default connection port", "option": "--port", "value": 27017, "comment": "specify port number - 27017 by default"},
	{ "name": "Replica set name prefix", "option": "--tReplSet", "value": "rpl_" , "comment": "arg is <setname>[/<optionalseedhostlist>]"},
	{ "name": "Database location", "option": "--tDBRootPath", "value": "./data", "comment": ""},
	{ "name": "Op log", "option": "--oplogSize", "value": 50, "comment": ""},
	{ "name": "Log path", "option": "--tLogPath", "value": "./logs" , "comment": ""},
	{ "name": "Log files prefix", "option": "--tLogFilesPrefix", "value": "log_" , "comment": ""}
#	{ "name": "", "option": "", "value": , "comment": ""},
]

def main(argv):
        if (len(argv) < 1):
                printUsage()
                return

	setServerPortCounter()
	checkAndCreateDBRootDir()
	checkAndCreateLogRootDir()
	startConfigServers()

def checkAndCreateDBRootDir():
	rootDirectory = getParameterValue("--tDBRootPath")
	checkAndCreateDir(rootDirectory)

def checkAndCreateLogRootDir():
	rootDirectory = getParameterValue("--tLogPath")
	checkAndCreateDir(rootDirectory)

def checkAndCreateDir(path):
	if (not os.path.exists(path)):
		os.makedirs(path)
	

def setServerPortCounter():
	global serverPortCounter

	serverPortCounter = int(getParameterValue("--port"))

def getFreePortNumber():
	# TODO check port free
	global serverPortCounter
	serverPortCounter += 1
	return serverPortCounter

def getHostname():
	return socket.gethostname()

def startConfigServers():
	global configServersString
 
	numServers = getParameterValue("--tConfigServers")
	dbPathTemplate = getParameterValue("--tDBRootPath") + "/" + "config_"
	logPathAndPrefix = getParameterValue("--tLogPath") + "/" + getParameterValue("--tLogFilesPrefix") + "config_"
	
	for i in xrange(1, numServers + 1):
		dbPath = dbPathTemplate + str(i)
		checkAndCreateDir(dbPath)
		newPort = str(getFreePortNumber())
		configServersString += getHostname() + ":" + newPort + ","
		command = "mongod --configsvr --dbpath " + dbPath + " --port " + newPort + " --fork --logappend --logpath " + logPathAndPrefix + str(i)
		print "Runing: " + command
		os.system(command)
	
	configServersString = configServersString[:len(configServersString)-1]


#def serializeParams(parameters):
#        serialParams = ''
#        for param in parameters:
#                if (param["value"] != None):
#                        serialParams += ' ' + param["option"]
#                        serialParams += ' "' + param["value"] + '"'
#        return serialParams


def initParameters(argv):
#        global path
#        path = argv[len(argv) - 1]
        for param in parameters:
                try:
                        index = argv.index(param["option"])
                        param["value"] = argv[index + 1]
                except Exception, e:
                        # Parameter not found: Keep the default.
                        pass

def getParameterValue(option):
	for param in parameters:
		if (param["option"] == option):
			return param["value"]

def printUsage():
        print "TODO"
        print ""
        print "Usage: mongo-test-env.py [options] "
        print ""

if __name__ == "__main__":
        main(sys.argv[1:])

