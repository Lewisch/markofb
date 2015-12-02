import sys
import json
import os
import urllib
import markovify
from Tkinter import *
import ttk

#First, two quick helper functions

#Checks if a file is empty
def check_text_file_empty(openedTextFilepath):
    if os.path.getsize(openedTextFilepath) > 0:
	return False
    else:
	return True

#Checks if n is an integer
def checkInt(n):
    try: 
        int(n)
        return True
    except ValueError:
        return False

#Opens the text file to be used for the data
def text_data_file():
    global f
    filepath = txtFile.get()
    if os.path.isfile(filepath):
        f = open(filepath, 'a')
        print "Using existing text data file"
    else:
        f = open(filepath,'a')
        print "Using new text data file"

#Opens the JSON file and converts it so Python can read it
def load_json(jsonfilepath):
    global currentJSON
    if os.path.isfile(jsonfilepath) == False:
        print jsonfilepath + "Not found"
    else:
        with open(jsonfilepath) as dataset:
            currentJSON = json.load(dataset)
    
#Writes the messages in your dataset to your text file
def write_messages(jsonData):
    mylen = len(jsonData['data'])
    #print mylen
    i=0
    while i < mylen:
        f.write(jsonData['data'][i]['message'].encode('utf-8'))
	print jsonData['data'][i]['message']
        i+=1
    f.close()

#For collect_from_fb
global nextfile
global newurl
global filelist
filelist = []
newurl = urllib.URLopener()

# Gets the link to the next page of JSON data
def getnextLink(jsondata):
    global nextLink
    if 'next' in jsondata.get('paging'):
        nextLink = str(jsondata.get('paging').get('next'))
	#print nextLink
	#print "next found"
    else:
	nextLink = "end"

# Gets the data from facebook and compiles into our text file
def collect_from_fb(firstURL):
    startingJSON = newurl.retrieve(firstURL, "0messages.json")
    startingFilepath = os.path.join(os.getcwd(), "0messages.json")
    filelist.append(startingFilepath)
    print filelist
    load_json(startingFilepath)
    print "starting json loaded"            
    i = 1
    write_messages(currentJSON)
    print "starting messages written"
    getnextLink(currentJSON)
    print nextLink
    #set to only get first 20 pages
    while nextLink != "end" and i < 20:
	getnextLink(currentJSON)
	if nextLink != "end":
	    nextFilePath = os.path.join(os.getcwd(),str(i) + "messages.json")
	    filelist.append(nextFilePath)
            try:
    	        nextfile = newurl.retrieve(nextLink, str(i) + "messages.json")
	    except IOError:
	        print "Error in collect_from_fb, Double check your JSON and get a new access code"
	        return		
	    load_json(nextFilePath)
            write_messages(currentJSON)
	else: 
	    print "All facebook data collected"
	    break
	i += 1

# Deletes files in a list and empties the list
def deleteFiles(listoffiles):
    for i in listoffiles:
	if os.path.isfile(i) == False:
	    print "File " + str(i) + " not found"
	    listoffiles.remove(i)
        else:
	    os.remove(i)
    listoffiles = []
	    

# Get raw text as string and build the model.
def buildModel(myfile):
    global text_model
    with open(myfile) as f1:
        text = f1.read()
    text_model = markovify.Text(text)

# Print n randomly-generated sentences of at most 140 characters
def printSentences(n):
    while checkInt(n) == False:
        print "Please enter a positive integer"
        printSentences(n)
    while int(n) < 1:
        print "Please enter a positive integer"
        printSentences(n)
    for i in range(int(n)):
	    #print i
            print(text_model.make_short_sentence(140))

# Decides whether to use an existing text file to make the sentences or get new data
def decideRoute(pid, acccode, flist):
    try:
	startingURL = "https://graph.facebook.com/" + pid + "/statuses?access_token=" + acccode
	print startingURL
	collect_from_fb(startingURL)
	#print "all data collected"
	buildModel(str(txtFile.get()))
	#print "model built"
	printSentences(int(numSentence.get()))
	deleteFiles(flist)       
    except IOError:
	if check_text_file_empty(str(txtFile.get())) == True:
	    print "Double check your inputs, unable to use data"
	else:
	    print "Access Code and/or Page ID invalid, using existing data"
	    buildModel(str(txtFile.get()))
	    printSentences(int(numSentence.get()))

def main(*args):
    text_data_file()
    decideRoute(PageID.get(), accessCode.get(), filelist)
    
root = Tk()
root.title("Markovify a Facebook page")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)


txtFile = StringVar()
PageID = StringVar()
numSentence = StringVar()
accessCode = StringVar()

txt_entry = ttk.Entry(mainframe, width=7, textvariable=txtFile)
txt_entry.grid(column=2, row=1, sticky=(W, E))

PageID_entry = ttk.Entry(mainframe, width=7, textvariable=PageID)
PageID_entry.grid(column=2, row=2, sticky=(W, E))

access_entry = ttk.Entry(mainframe, width=7, textvariable=accessCode)
access_entry.grid(column=2, row=3, sticky=(W, E))

numSentence_entry = ttk.Entry(mainframe, width=7, textvariable=numSentence)
numSentence_entry.grid(column=2, row=4, sticky=(W, E))

ttk.Label(mainframe, text="Enter path for your txt File to use").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="Enter the ID for your facebook page (should be a number)").grid(column=3, row=2, sticky=W)
ttk.Label(mainframe, text="Enter your access token").grid(column=3, row=3, sticky=W)
ttk.Label(mainframe, text="Enter number of sentences").grid(column=3, row=4, sticky=W)

ttk.Button(mainframe, text="Markovify", command=main).grid(column=3, row=5, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

txt_entry.focus()
root.bind('<Return>', main)

root.mainloop()
