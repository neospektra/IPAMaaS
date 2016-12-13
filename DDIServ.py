#!/usr/bin/python
# -Matt Dell-
import BluecatIPAM

from flask import Flask, jsonify, request

app = Flask(__name__)
#Each @app.route('URL') Is a URL and instructions to run when that URL is called are below

@app.route('/REST/SysInfo', methods=['GET'])
def GetInfo():
	MyToken = BluecatIPAM.GetToken()
	myTest = "Test" + BluecatIPAM.getSysInfo(MyToken)
	if len(MyTest) == 0:
		abort(404)
	return myTest
@app.route('/REST/DeleteIP', methods= ['GET'])
def delIP():
	#QueryString from URL Args 
	MyIP = request.args.get('IP')
	MyToken = BluecatIPAM.GetToken()
	MyConfID = str(BluecatIPAM.GetConfigID(MyToken))
	response = BluecatIPAM.DeleteDeviceInstance(MyToken, MyConfID, MyIP)
	JsonReturn = [ {"Response" : response}]
	BluecatIPAM.logout(MyToken)
	return jsonify(JsonReturn)
@app.route('/REST/GetIP', methods=['GET'])
def GetIP():
	MyIP = request.args.get('ip')
	#Auth to the Bluecat Platform
	MyToken = BluecatIPAM.GetToken()
	#Get the Bluecat Configuration ID
	MyConfID = str(BluecatIPAM.GetConfigID(MyToken))
	#Now get the DNS View assoicated with the view defined in BluecatIPAM.py
	print (MyConfID)
	print (MyIP)
	response = BluecatIPAM.getIP4Address(MyToken, MyIP, MyConfID)
	return (response)
@app.route('/REST/AddIP', methods=['GET'])
def AddIP():	
	#Url QueryString for IPv4 Network Lookup	
	hint = request.args.get('hint')
	#Hostname Querystring to set new IP
	MyHost = request.args.get('hostname')
	MyInstant = int(request.args.get('instant'))
	#Auth to the Bluecat Platform
	MyToken = BluecatIPAM.GetToken()
	#Get the Bluecat Configuration ID
	MyConfID = str(BluecatIPAM.GetConfigID(MyToken))
	#Look for a matching IPv4 Subnet
	NetInfo = BluecatIPAM.getIP4ByName(MyToken, hint, MyConfID)
	#Now get the DNS View assoicated with the view defined in BluecatIPAM.py
	MyViewID = str(BluecatIPAM.GetViewID(MyToken, MyConfID))
	#Pull CIDR from IPv4 search
	CIDR = NetInfo[1]
	#Grab ID of subnet we want to look for IP
	ParentID = str(NetInfo[0])
	#Set the Subnet for printing
	Subnet = NetInfo[2]
	#Find the next available IP address in subnet with ParentID above
	MyIP = BluecatIPAM.getNextIP4(MyToken, ParentID)
	#Trim up the quotes
	MyDisplayIP = MyIP[1:-1]
	#print (MyInstant)
	#Add error checker for not defining instant. below doesn't work.
	#if MyInstant is None:
	#	MyInstant == 0
	#Next should we try and update DNS immediately, or wait till the scheduled push. 
	#Instant = 1 requests take longer
	
	if MyInstant == 0:
		NewIPID = BluecatIPAM.AssignNewIP4(MyToken, MyConfID, MyIP, MyHost, MyViewID)
		print (NewIPID)
		JsonReturn = [ {"Subnet" : Subnet,"Mask" : CIDR, "IP Address" : MyDisplayIP, "Hostname" : MyHost, "Node Type" : "TBD","DeviceID" : NewIPID}]
	else:
		NewIPID = BluecatIPAM.addDeviceInstance(MyToken, MyConfID, MyIP, MyHost)
		JsonReturn = [ {"Subnet" : Subnet,"Mask" : CIDR, "IP Address" : MyDisplayIP, "Hostname" : MyHost, "Node Type" : "TBD","DeviceID" : NewIPID}]
	if NewIPID == "":
		return ("Failed to assign IP: " + MyIP)
	BluecatIPAM.logout(MyToken)
	return jsonify(JsonReturn)
#Sample 404 Error
#	if len(task) == 0:
#		abort(404)
#End Sample#
#	return jsonify({'task': task[0]})
if __name__ == '__main__':
	app.run(debug=True)
