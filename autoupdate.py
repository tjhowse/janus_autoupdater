#!/usr/bin/python
#
# Checks http://archive.janusvr.com/ for a newer version of JanusVR than the one installed.
# Downloads the latest OS-appropriate installer and prompts the user to complete the installation.
#
# Copyright 2016 Travis Howse
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2,os,subprocess
from sys import platform as _platform

archiveURL = "http://archive.janusvr.com/"
version = "v1.02"

def getOS():
	if _platform == "linux" or _platform == "linux2":
		return "Linux"
	elif _platform == "darwin":
		return "Mac"
	elif _platform == "win32":
		return "Windows"
	print("Can't detect OS version. Abort!")
	exit()

def saveInstalledVersion(version):
	try:
		f = open("janus_version",'w')
		f.write(version)
		f.close()
	except:
		print("Failed to save installed version to file. Check disk write permissions.")
	
def getInstalledVersion():
	if not os.path.isfile("janus_version"):
		return "0.0"
	try:
		f = open("janus_version",'r')
		version = f.read()
		f.close()
	except:
		print("Failed to get installed version from file. Check disk read permissions.")
		return "0.0"
	return version
	
def getVersions():
	versions = []
	page = urllib2.urlopen(archiveURL)
	for line in page:
		if line.startswith("<li>") and line.endswith("</li>\n"):
			versions += [line[14:line.index("/'>V")]]
	if len(versions) == 0:
		print("Failed to get available versions."+archiveURL+" down, or format has changed.")
		exit()
	return versions

def getInstallerURL(version,OS):
	downloadsURL = archiveURL+"V"+version
	page = urllib2.urlopen(downloadsURL)
	for line in page:
		if OS in line:
			return downloadsURL+"/"+line[line.index("janus"):line.index("\">")]
	print("Failed to get available versions."+archiveURL+" down, or format has changed.")
	exit()
	
def checkNewerVersion(latestOnWeb,current):
	(webMaj,webMin) = latestOnWeb.split('.')
	(curMaj,curMin) = current.split('.')
	if int(webMaj) > int(curMaj):
		return True
	elif webMaj == curMaj and int(webMin) > int(curMin):
		return True
	return False

def downloadInstaller(version,OS):
	downloadURL = getInstallerURL(version,OS)
	
	file_name = downloadURL.split('/')[-1]
	u = urllib2.urlopen(downloadURL)
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break

		file_size_dl += len(buffer)
		f.write(buffer)
		status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		status = status + chr(8)*(len(status)+1)
		print status,
	f.close()
	return file_name
	
if __name__ == "__main__":
	print("JanusVR autoupdater, version "+version)
	OS = getOS()
	versions = getVersions()
	latestVersion = versions[-1]
	currentVersion = getInstalledVersion()
	if not checkNewerVersion(latestVersion,currentVersion):
		print("You've got the latest version of JanusVR according to "+archiveURL)
		exit()
	print("Newer version found, downloading JanusVR version V"+latestVersion)
	fileName = downloadInstaller(latestVersion,OS)
	saveInstalledVersion(latestVersion)
	print("Installing JanusVR version V"+latestVersion+": "+fileName)
	if OS == "Windows":
		os.startfile(fileName)
	elif OS == "Linux":
		subprocess.call(["xdg-open", fileName])
	elif OS == "Mac":
		os.system("open "+fileName)
	
