import sys
import subprocess

if len(sys.argv) != 2:
    print("Needs at least 1 file")
    sys.exit(1)

fileName = sys.argv[1]

#First must obtain list of streams in input file
command = 'ffmpeg -i "' + fileName + '"'
print(command)

result = subprocess.run(command, capture_output=True, shell=True)

if not result.stdout:
    output = result.stderr.decode('utf-8')
else:
    output = result.stdout.decode('utf-8')

lines = output.split('\n')

vStreams, aStreams, sStreams, attachments, oStreams = 0, 0, 0, 0, 0

for line in lines:
     line = line.strip()
     if (line.startswith('Stream')):
         print(line)
         if ('Video:' in line):
             vStreams+=1
         elif ('Audio:' in line):
             aStreams+=1
         elif ('Subtitle:' in line):
             sStreams+=1
         elif ('Attachment:' in line):
             attachments+=1
         else:
             oStreams+=1

print('-------------------------------------')
print(str(vStreams) + " video streams found")
print(str(aStreams) + " audio streams found")
print(str(sStreams) + " subtitle streams found")
print(str(attachments) + " attachments")
print(str(oStreams) + " other streams found")
print('-------------------------------------')

if (oStreams != 0):
    print("Unmapped streams found. Aborting.")
    sys.exit(1)
if (aStreams < 2):
    print("File only contains 1 audio track. Aborting.")
    sys.exit(1)


#Have the data we need, start building ffmpeg command
#map all video streams unchanged
command += ' -map 0:v'

#swap the order of the audio tracks and change the default flags
command += ' -map 0:a:1'
command += ' -map 0:a:0'
command += ' -disposition:a:0 default -disposition:a:1 0'

#if there are more than 2 audio streams, copy them over without changing order
for x in range(2, aStreams):
    command += ' -map 0:a:'+str(x)

#map the Subtitle streams
#   1 subtitle track is copied over unchanged
#   2 or more subtitle tracks swaps order of 1st and 2nd. Change default to new 1st track
if sStreams==1:
    command += ' -map 0:s'
elif sStreams >=2:
    command += ' -map 0:s:1'
    command += ' -map 0:s:0'
    command += ' -disposition:s:0 default -disposition:s:1 0'
for x in range(2, sStreams):
    command += ' -map 0:s:'+str(x)

#map attachment streams next
if (attachments != 0):
    command += ' -map 0:t'

#only need to mux, not encode
command += ' -c copy'
#output path
outputFile = 'Output\\' + fileName
command += ' "' + outputFile + '"'

print(command)
result = subprocess.run(command, shell=True)

print('\n' + command)
