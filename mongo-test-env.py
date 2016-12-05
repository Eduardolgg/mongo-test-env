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
from pymongo.errors import *

serverPortCounter = None
configServersString = ""
defaultPort = 27017

# TODO: Too dark, change
parameters = [
	{ "name" : "Number of replica sets in the cluster", "option": "--replicaSetNumber", "value": 2, "single": False },
	{ "name": "Replica Set Size", "option": "--replicaSetSize", "value": 2 , "single": False },
	{ "name": "Replica set name prefix", "option": "--replSet", "value": "rpl_" , "comment": "arg is <setname>[/<optionalseedhostlist>]", "single": False },
	{ "name": "Arviters per repica set", "option": "--arviters", "value": 1, "single": False },
	{ "name": "Shards Routers", "option": "--routers", "value": 2, "single": False },
	{ "name": "Config Servers", "option": "--configServers", "value": 3, "single": False },
	{ "name": "Default connection port", "option": "--port", "value": defaultPort, "comment": "specify port number - 27017 by default", "single": False },
	{ "name": "Database location", "option": "--dbRootPath", "value": "./data", "comment": "", "single": False },
	{ "name": "Log path", "option": "--logPath", "value": "./logs" , "comment": "", "single": False },
	{ "name": "Log files prefix", "option": "--logFilesPrefix", "value": "log_" , "comment": "", "single": False },
	{ "name": "Debug option", "option": "--debug", "value": False , "comment": "Does not execute the commands, only shows them", "single": True },
	
	{ "name": "Config Server options", "option": "--cs-options", "value": "", "comment": "", "single": False },
	{ "name": "Replica set (mongod) options", "option": "--rs-options", "value": "--smallfiles --oplogSize 50", "comment": "", "single": False },
	{ "name": "MongoDB Sharded Cluster Query Router (mongos) options", "option": "--sh-options", "value": "", "comment": "", "single": False }
#	{ "name": "", "option": "", "value": , "comment": ""},
]

def main(argv):
	if (len(argv) < 1):
		printUsage()
		return

	initParameters(argv)

	dbRootPath = getParameterValue("--dbRootPath")
	logPath = getParameterValue("--logPath")
	logFilePrefix = getParameterValue("--logFilesPrefix")
	replicaSetNamePrefix = getParameterValue("--replSet")
	replicaSets = getParameterValue("--replicaSetNumber")
	replicaSetSize  = getParameterValue("--replicaSetSize")
	arbiters = getParameterValue("--arviters")
	replicaSetOptions = getParameterValue("--rs-options")
	routerOptions  = getParameterValue("--sh-options")
	#  = getParameterValue()

	setServerPortCounter()
	checkAndCreateDBRootDir()
	checkAndCreateLogRootDir()
	startConfigServers()
	replicaSetInfo = startReplicaSets(dbRootPath, logPath, logFilePrefix, replicaSetNamePrefix, replicaSets, replicaSetSize, arbiters, replicaSetOptions)
	startShardRouters(configServersString, logPath, logFilePrefix, routerOptions)

	startAutoConf(replicaSetInfo)

def checkAndCreateDBRootDir():
	rootDirectory = getParameterValue("--dbRootPath")
	checkAndCreateDir(rootDirectory)

def checkAndCreateLogRootDir():
	rootDirectory = getParameterValue("--logPath")
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
 
	numServers = getParameterValue("--configServers")
	dbPathTemplate = getParameterValue("--dbRootPath") + "/" + "config_"
	logPathAndPrefix = getParameterValue("--logPath") + "/" + getParameterValue("--logFilesPrefix") + "config_"
	configServerOptions = getParameterValue("--cs-options")
	
	
	for i in xrange(1, int(numServers) + 1):
		dbPath = dbPathTemplate + str(i)
		checkAndCreateDir(dbPath)
		newPort = str(getFreePortNumber())
		configServersString += getHostname() + ":" + newPort + ","
		command = "mongod --configsvr --dbpath " + dbPath + " --port " + newPort + " --fork --logappend --logpath " + logPathAndPrefix + str(i) + " " + configServerOptions
		runCommand(command)

	configServersString = configServersString[:len(configServersString)-1]


def startReplicaSets(dbRootPath, logPath, logFilePrefix, replicaSetNamePrefix, replicaSets, replicaSetSize, replicaSetArbiters, replicaSetOptions):
	replicaSetInfo = []
	for suit in xrange(1, int(replicaSets) + 1):
		replicaSetName = replicaSetNamePrefix + str(suit)
		serverCount = 0
		replicaSet_n_info = {"_id": replicaSetName, "members": [] }
		for server in xrange(1, int(replicaSetSize) + 1):
			port = str(getFreePortNumber())
			dbPath = dbRootPath + "/" + replicaSetNamePrefix + "replica_" + "suit_" + str(suit) + "_server_" + str(server)
			checkAndCreateDir(dbPath)
			logFile = logPath + "/" + logFilePrefix + "replica_" + "suit_" + str(suit) + "_server_" + str(server)
			startMongodServer(dbPath, logFile, replicaSetName, port, replicaSetOptions)
			replicaSet_n_info["members"].append({ "_id": serverCount, "host": getHostname() + ":" + port})
			serverCount += 1
		for server in xrange(1, int(replicaSetArbiters) + 1):
			port = str(getFreePortNumber())
			dbPath = dbRootPath + "/" + replicaSetNamePrefix + "arbiter_" + "suit_" + str(suit) + "_server_" + str(server)
			checkAndCreateDir(dbPath)
			logFile = logPath + "/" + logFilePrefix + "arbiter_" + "suit_" + str(suit) + "_server_" + str(server)
			startMongodServer(dbPath, logFile, replicaSetName, port, replicaSetOptions)
			replicaSet_n_info["members"].append({ "_id": serverCount, "host": getHostname() + ":" + port, "arbiterOnly": True})
			serverCount += 1
		replicaSetInfo.append(replicaSet_n_info)
	return replicaSetInfo

def startShardRouters(configServersList, logPath, logFilePrefix, routerOptions):
	routers = int(getParameterValue("--routers"))
	for i in xrange(1, routers+1):
		if (i == 1):
			port = str(defaultPort)
		else:
			port = str(getFreePortNumber())
		logFile = logPath + "/" + logFilePrefix + "router_" + str(i) 
		command = "mongos --configdb " + configServersList + " --fork --logappend --logpath " + logFile + " --port " + port + " " + routerOptions
		runCommand(command)


def startMongodServer(dbPath, logFile, replicaSetName, port, replicaSetOptions):
	command = "mongod --shardsvr --replSet " + replicaSetName + " --dbpath " + dbPath 
	command += " --logappend --logpath " + logFile 
	command += " --port " + port + " --fork " + replicaSetOptions
	runCommand(command)

def startAutoConf(replicaSetInfo):
	autoConfReplicaSets(replicaSetInfo)
	autoConfRouters(replicaSetInfo)

def autoConfReplicaSets(replicaSetInfo):
	for replicaSet in replicaSetInfo:
		client = MongoClient(replicaSet["members"][0]["host"])
		try:
			runServerAdminCommand(client, {"replSetInitiate": replicaSet})
		except ConfigurationError:
			print("Replica set config error: " + replicaSet)
		except ConnectionFailure:
			print("Connecting to replica set Error: " + replicaSet)


def autoConfRouters(replicaSetInfo):
	for replicaSet in replicaSetInfo:
		client = MongoClient(getHostname())
		try:
			members = memberUri(replicaSet)
			runServerAdminCommand(client, { "addShard": members })
		except ConfigurationError:
			print("Shard config error: " + replicaSet)
		except ConnectionFailure:
			print("Connecting to addShard error: " + replicaSet)

def memberUri(replicaSet):
	return replicaSet["_id"] + "/" + replicaSet["members"][0]["host"]

def runServerAdminCommand(client, command):
	if (isDebugEnabled()):
		print "db._adminCommand(" + str(command) + ")"
	else:
		client.admin.command(command)

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
	if (isDebugEnabled()):
		print command
	else:
		print "Running: " + command
		os.system(command)

def isDebugEnabled():
	return getParameterValue("--debug") != False

def printUsage():
        print "TODO"
        print ""
        print "Usage: mongo-test-env.py [options] "
        print ""

if __name__ == "__main__":
        main(sys.argv[1:])

