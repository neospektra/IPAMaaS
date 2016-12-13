#!/usr/bin/python
####Copyright 2016 Matt Dell -First Data GIO
#Global Def

import http.client
import json
from sys import argv
import socket
import struct
from socket import inet_ntoa
from struct import pack

######Global Variables######
BluecatConType = "HTTP"
BluecatURL = "192.168.1.8"
BluecatAPIUser = "api"
BluecatAPIPass = "api"
#Set below to Configuration Name#
BluecatConfigName = "FDC%20Organization"
#BluecatConfigName = "Test"
BluecatViewName = "Internal"
BluecatDefaultDomain = "1dc.com"
debug = 1
#Set below to 1 for HTTPS
HTTPS = 0

######## Global Connect Utility ########
def conAPI(MyToken,MyConType,MyConData):
	if HTTPS == 0:
		conn = http.client.HTTPConnection(BluecatURL)
	else:
		conn = http.client.HTTPSConnection(BluecatURL)
	#If MyToken is null, it must be a auth request
	if MyToken == "":
		headers = {
			'cache-control': "no-cache"
			}
		conn.request(MyConType, MyConData, headers=headers)
		res = conn.getresponse()
		data = res.read()
		value = data.decode("utf-8")
		return value
	#Otherwise process connection request
	else:
		headers = {
			'authorization': "BAMAuthToken: " + MyToken,
			'cache-control': "no-cache"
			}
		conn.request(MyConType, MyConData, headers=headers)
		res = conn.getresponse()
		data = res.read().decode('utf-8')		
		return data

#Get Subnet for CIDR#
#TODO Add CIDR TO MASK
#

########Get Auth################
def GetToken():
	list1 = []
	MyConType = "GET"
	MyConData = "/Services/REST/v1/login?username="+BluecatAPIUser +"&password=" +BluecatAPIPass
	MyToken =""
	value = conAPI(MyToken,MyConType,MyConData)
	remspace = value.split(" ")
	for val in remspace:
		list1.append(val)
	myToken = (list1[3])
	return myToken
###########END Auth############

#### Grab the ID for the defined configuration name###
def GetConfigID(MyToken):
	MyConType = "GET"
	MyConData = "/Services/REST/v1/getEntityByName?parentId=0&name=" + BluecatConfigName +"&type=Configuration"
	data = conAPI(MyToken, MyConType, MyConData)
	obj = json.loads(data)
	ConfID = obj['id']
	return ConfID
#### Get the ID of the DNS View in question####

def GetViewID(MyToken,MyConfID):
	MyConType = "GET"
	MyConData = "/Services/REST/v1/getEntityByName?parentId=" + MyConfID +"&name=" + BluecatViewName +"&type=View"
	data = conAPI(MyToken, MyConType, MyConData)
	obj = json.loads(data)
	ViewID = obj['id']
	#print (ViewID)
	return ViewID

		
####Test Sub#####
def getSysInfo(MyToken):
	MyConData = "/Services/REST/v1/getSystemInfo"
	MyConType = "GET"
	data = conAPI(MyToken, MyConType, MyConData)
	print(data)
####End Test Sub####

####Get IPv4 Network by Hint(name)####
def getIP4ByName(MyToken,hint,MyConfID):
	list2 = []
	MyConType = "GET"
	MyConData = "/Services/REST/v1/getIP4NetworksByHint?containerId="+MyConfID+"&start=0&count=10&options=hint%3D"+hint +"&Content-Type=application%2Fjson"
	data = conAPI(MyToken, MyConType, MyConData)
	obj = json.loads(data)
	ParentID = obj[0]['id']
	#print (obj)
	MyName = obj[0]['name']
	MyProperties = obj[0]['properties'].split("|")
	MyCIDR = MyProperties[0]
	MyLen = MyCIDR.split("/")
	CIDR = MyLen[1]
	Subnet1 = MyLen[0]
	Subnet2 = Subnet1.split("=")
	Subnet = Subnet2[1] + "/" + CIDR
	return (ParentID,CIDR,Subnet,MyName)
	
#Read IPv4 Address passed as IP
def getIP4Address(MyToken,MyIP,MyConfID):
	MyConType = "GET"
	MyConData = "/Services/REST/v1/getIP4Address?containerid=" + MyConfID + "&address=" + MyIP
	data = conAPI(MyToken, MyConType, MyConData)	
	#print (MyConData)
	return (data)
#Get Next Available IPv4 Address in network X	
def getNextIP4(MyToken,MyID):
	MyConType = "GET"
	MyConData = "/Services/REST/v1/getNextIP4Address?parentId="+MyID
	data = conAPI(MyToken, MyConType, MyConData)
	return data
	
	
### Add New IP###
def AssignNewIP4(MyToken,MyConfID,MyIP,MyHost,MyViewID):
	MyHostInfo = MyHost + "," + MyViewID + "," + "true,false"
	MyNewIP = MyIP[1:-1]
	MyConData = "/Services/REST/v1/assignIP4Address?configurationId=" + MyConfID + "&ip4Address=" + MyNewIP + "&hostInfo=" + MyHostInfo + "&action=MAKE_STATIC"
	MyConType = "POST"
	data = conAPI(MyToken, MyConType, MyConData)
	#print (myConData)
	#print (data)
	return data
# Add IP and hostname to DNS Instantly
def addDeviceInstance(MyToken,MyConfID,MyIP,MyHost):
	MyNewIP = MyIP[1:-1]
	MyConType = "POST"
	MyConData = "/Services/REST/v1/addDeviceInstance?configName=" + BluecatConfigName + "&recordName=" + MyHost + "&viewName=" +BluecatViewName + "&zoneName=" + BluecatDefaultDomain + "&ipAddressMode=PASS_VALUE&ipEntity=" + MyNewIP
	data = conAPI(MyToken, MyConType, MyConData)
	print (data)
	return data
def DeleteDeviceInstance(MyToken,MyConfID,MyIP):
	MyDelIP = MyIP[1:-1]
	MyConType = "DELETE"
	MyConData = "/Services/REST/v1/deleteDeviceInstance?configName=" + BluecatConfigName + "&identifier=" + MyDelIP
	data = conAPI(MyToken, MyConType,MyConData)
	print (data)
	if data == "":
		return "Success"
	else:
		return data

def logout(MyToken):
	MyConType = "GET"
	MyConData = "/Services/REST/v1/logout"
	data = conAPI(MyToken, MyConType, MyConData)
	return data
	
######BEGIN Main###########
##Commented out for REST Server##
#Start by getting token
#MyToken = GetToken()
#Hint = all or portion of subnet name
#hint = argv[1]
#MyHost = fqdn to add
#MyHost = "testhost.1dc.com"#argv[2]
#MyConfID = str(GetConfigID(MyToken))
#MyViewID = str(GetViewID(MyToken, MyConfID))
#NetInfo = getIP4ByName(MyToken, hint, MyConfID)
#ParentID = str(NetInfo[0])
#CIDR = NetInfo[1]
#Subnet = NetInfo[2]
#MyIP = getNextIP4(MyToken,ParentID)
#NewIPID = AssignNewIP4(MyToken, MyConfID, MyIP, MyHost, MyViewID)
#if debug == 1:
#	print ("Found IP Address to assign: " + MyIP)
#	print ("From " + Subnet)
#	print ("With Network Name :" + NetInfo[3])
#	print ("Assigning It To Hostname:" + MyHost)
#	print ("New host ID: " + NewIPID)
#	print ("Netmask: " + CIDR)

#print (logout(MyToken))
