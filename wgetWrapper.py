import os
import sys
import glob

def pathPrefix():
    homeDir = os.getcwd()
    return homeDir + "\\Downloading\\"

def pathFromURL(url):
    path = url.replace("%20"," ")
    path = path.replace("http://", "")
    path = path.replace("https://", "")
    path = path.replace("/", "\\")
    path = path.replace("%5b", "[")
    path = path.replace("%5d", "]")
    path = path.replace(":", "+")
    #path = path[path.find(":")+1:]
    path = pathPrefix() + path
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def listFiles(path):
    return glob.glob(path + '\**\*.*', recursive=True)

def getHash(path):
    #print("Hashing File:"+path)
    return str(os.stat(path).st_size)

def updateHashFile(path):
    print("Updating hash:"+path)
    fileList = listFiles(path)
    f = open(path+"hash.txt","w")
    for file in fileList:
        if not file.endswith("hash.txt"):
            f.write(str(file) + "|" + getHash(file) + "\n")
    f.close()

def checkHashFileChanged(path):
    print("Checking if any data was changed:"+path)
    #Open Hash file for reading
    f = open(path+"hash.txt","r")
    lines = f.readlines()

    #Check if the number of files has changed
    #Subtract one for hash.txt
    numFiles = len(listFiles(path)) - 1
    if numFiles != len(lines):
        return True
    
    for line in lines:
        filePath = line.split("|")[0]
        fileHash = line.split("|")[1].rstrip()
        newHash = getHash(filePath)
        if fileHash != newHash:
            return True
    return False
    
if len(sys.argv) != 2:
    print("Needs 1 link or file")
    sys.exit(1)

link = sys.argv[1]
wgetArgs = ''
wgetArgs += ' --continue'
wgetArgs += ' --show-progress'
wgetArgs += ' --recursive'
wgetArgs += ' --no-parent'
wgetArgs += ' --no-check-certificate'
wgetArgs += ' --directory-prefix=' + pathPrefix()

command = 'wget ' + wgetArgs + ' ' + link
print("Command:" + command)
print("Path:" + pathFromURL(link))

incomplete = True
while(incomplete):
    updateHashFile(pathFromURL(link))
    print("running wget")
    stream = os.popen(command)
    output = stream.read()
    incomplete = checkHashFileChanged(pathFromURL(link))

print ("done")

