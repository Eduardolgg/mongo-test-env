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
defaultPort = 27017

# TODO: Too dark, change
parameters = [
        { "name" : "Number of replica sets in the cluster", "option": "--tReplicaSetNumber", "value": 2, "single": False },
        { "name": "Replica Set Size", "option": "--tReplicaSetSize", "value": 2 , "single": False },
	{ "name": "Replica set name prefix", "option": "--tReplSet", "value": "rpl_" , "comment": "arg is <setname>[/<optionalseedhostlist>]", "single": False },
        { "name": "Arviters per repica set", "option": "--tArviters", "value": 1, "single": False },
        { "name": "Shards Routers", "option": "--tRouters", "value": 2, "single": False },
	{ "name": "Config Servers", "option": "--tConfigServers", "value": 3, "single": False },
	{ "name": "Default connection port", "option": "--port", "value": defaultPort, "comment": "specify port number - 27017 by default", "single": False },
	{ "name": "Database location", "option": "--tDBRootPath", "value": "./data", "comment": "", "single": False },
	{ "name": "Op log", "option": "--oplogSize", "value": "50", "comment": "", "single": False },
	{ "name": "Log path", "option": "--tLogPath", "value": "./logs" , "comment": "", "single": False },
	{ "name": "Log files prefix", "option": "--tLogFilesPrefix", "value": "log_" , "comment": "", "single": False },
	{ "name": "Debug option", "option": "--debug", "value": False , "comment": "Does not execute the commands, only shows them", "single": True }
#	{ "name": "", "option": "", "value": , "comment": ""},
]

def main(argv):
        if (len(argv) < 1):
                printUsage()
                return

	initParameters(argv)

	dbRootPath = getParameterValue("--tDBRootPath")
	logPath = getParameterValue("--tLogPath")
	logFilePrefix = getParameterValue("--tLogFilesPrefix")
	replicaSetNamePrefix = getParameterValue("--tReplSet")
	replicaSets = getParameterValue("--tReplicaSetNumber")
	replicaSetSize  = getParameterValue("--tReplicaSetSize")
	arbiters = getParameterValue("--tArviters")
	#  = getParameterValue()
	#  = getParameterValue()

	setServerPortCounter()
	checkAndCreateDBRootDir()
	checkAndCreateLogRootDir()
	startConfigServers()
	startReplicaSets(dbRootPath, logPath, logFilePrefix, replicaSetNamePrefix, replicaSets, replicaSetSize, arbiters)
	startShardRouters(configServersString, logPath, logFilePrefix)

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

#TODO add parameters
def startConfigServers():
	global configServersString
 
	numServers = getParameterValue("--tConfigServers")
	dbPathTemplate = getParameterValue("--tDBRootPath") + "/" + "config_"
	logPathAndPrefix = getParameterValue("--tLogPath") + "/" + getParameterValue("--tLogFilesPrefix") + "config_"
	
	for i in xrange(1, int(numServers) + 1):
		dbPath = dbPathTemplate + str(i)
		checkAndCreateDir(dbPath)
		newPort = str(getFreePortNumber())
		configServersString += getHostname() + ":" + newPort + ","
		command = "mongod --configsvr --dbpath " + dbPath + " --port " + newPort + " --fork --logappend --logpath " + logPathAndPrefix + str(i)
		runCommand(command)
	configServersString = configServersString[:len(configServersString)-1]


def startReplicaSets(dbRootPath, logPath, logFilePrefix, replicaSetNamePrefix, replicaSets, replicaSetSize, replicaSetArbiters):
	for suit in xrange(1, int(replicaSets) + 1):
		replicaSetName = replicaSetNamePrefix + str(suit)
		#TODO: Refactor
		for server in xrange(1, int(replicaSetSize) + 1):
			port = str(getFreePortNumber())
			dbPath = dbRootPath + "/" + replicaSetNamePrefix + "replica_" + "suit_" + str(suit) + "_server_" + str(server)
			checkAndCreateDir(dbPath)
			logFile = logPath + "/" + logFilePrefix + "replica_" + "suit_" + str(suit) + "_server_" + str(server)
			startMongodServer(dbPath, logFile, replicaSetName, port)
		for server in xrange(1, int(replicaSetArbiters) + 1):
			port = str(getFreePortNumber())
			dbPath = dbRootPath + "/" + replicaSetNamePrefix + "arbiter_" + "suit_" + str(suit) + "_server_" + str(server)
			checkAndCreateDir(dbPath)
			logFile = logPath + "/" + logFilePrefix + "arbiter_" + "suit_" + str(suit) + "_server_" + str(server)
			startMongodServer(dbPath, logFile, replicaSetName, port)

def startShardRouters(configServersList, logPath, logFilePrefix):
	routers = int(getParameterValue("--tRouters"))
	for i in xrange(1, routers+1):
		if (i == 1):
			port = str(defaultPort)
		else:
			port = str(getFreePortNumber())
		logFile = logPath + "/" + logFilePrefix + "router_" + str(i) 
		command = "mongos --configdb " + configServersList + " --fork --logappend --logpath " + logFile + " --port " + port
		runCommand(command)


def startMongodServer(dbPath, logFile, replicaSetName, port):
	opLogSize = getParameterValue("--oplogSize")
	command = "mongod --shardsvr --replSet " + replicaSetName + " --dbpath " + dbPath 
	command += " --logappend --logpath " + logFile 
	command += " --port " + port + " --fork --oplogSize " + opLogSize
	runCommand(command)

#def serializeParams(parameters):
#        serialParams = ''
#        for param in parameters:
#                if (param["value"] != None):
#                        serialParams += ' ' + param["option"]
#                        serialParams += ' "' + param["value"] + '"'
#        return serialParams

def initParameters(argv):
        for param in parameters:
                try:
                        index = argv.index(param["option"])
			if (param["single"]):
				param["value"] = ""
			else:
	                        param["value"] = argv[index + 1]
                except Exception, e:
                        # Parameter not found: Keep the default.
                        pass

def getParameterValue(option):
	for param in parameters:
		if (param["option"] == option):
			return param["value"]

def runCommand(command):
	debug = getParameterValue("--debug") != False
	if (debug):
		print command
	else:
		print "Running: " + command
		os.system(command)

def printUsage():
        print "TODO"
        print ""
        print "Usage: mongo-test-env.py [options] "
        print ""

if __name__ == "__main__":
        main(sys.argv[1:])

