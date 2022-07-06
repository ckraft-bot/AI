############################################################ SUMMARY AND INTRO ############################################################

# Python 3.9.5 64 bit

from distutils import extension
from email.mime import audio
from unittest import removeResult
import librosa
import torch 
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer  # pip install transformers

import os, sys
from datetime import date, timedelta, datetime
import glob
from pathlib import Path

import cx_Oracle # pip install cx_Oracle
import sqlalchemy # pip install sqlalchemy
import pandas as pd # try on jupyter notebook; note-- in vs code you won't be able to preview the columns or headers.
import numpy as np
############################################################ SET UP ############################################################
# Create a dummy df as template, add the cols (PCS_ID, TRANSCRIPTION, MODIFIED_DATETIME)

Columns_list = ['PCS_ID', 'TRANSCRIPTION', 'MODIFIED_DATETIME']
Dummy_df = pd.DataFrame(columns = Columns_list)
print(Dummy_df)

# Creating a var called "now", when it comes to transcription stage, they can be timestamped
from datetime import datetime

# Current date and time
now = datetime.now()
print(now)


# Extracting password from elsewhere
#import csv
#with open(r'C:\Users\ckraft\Desktop\My Experiments\Mima.csv') as f:
    #reader = csv.reader(f)
    #next(reader)
    #for row in reader:
        #Its_a_secret = 'Secret: ' + row[2]  
#print(Its_a_secret)


# Accessing oracle 

DATABASE = "BBPROD"
SCHEMA   = "CKRAFT"
PASSWORD = "<it's a secret>"
connstr  = "oracle://{}:{}@{}".format(SCHEMA, PASSWORD, DATABASE)
conn     = sqlalchemy.create_engine(connstr)




# If you want to create a table w/o the dbeaver GUI
"""
CREATE TABLE OPS_REPORTING.PCS_TRANSCRIPTIONS (
PCS_ID NUMBER(20,0),
TRANSCRIPTION CLOB,
MODIFIED_DATETIME DATE
);
"""

query = """
    select * from OPS_REPORTING.PCS_TRANSCRIPTIONS
        """
data = pd.read_sql(query, conn)
print(data.head())
data.columns


### the full Oracle DB Client must be installed. They do not do this by default when they install Oacle SQL Developer. ### 
### An easy way to check this: windows key > type "sql plus" > if an app doesn't pop up, you don't have it. ###

############################################################ OUTLINE ############################################################


"""
1. Connect to Oracle
2. Create a schema and a table with 3 columns: ID, transcription, date modified (which timestamps the transctiption task) in dbeaver
3. Create a dummy df with the necessary columns for short term memory
4. Loop trough audio files
5. Create an array of the looped files
6. Iterate the elemnte in the array one at a time to be transcribed
7. Run transcribe machine
5. Transcription outputs fill the dummy table
6. Write the INSERT query (look at Options for writing to SQL database)

Options for writing to SQL database:
1. For a single line, write the "INSERT" sql.
2. In bulk, write each line to a pandas dataframe, then use Pandas to write the dataframe to the SQL table. 
    my_data_frame.to_sql(TableName, engine, chunksize=<yourParameterLimit>, method='multi')
    here is a method parameter in pandas.to_sql() where you can define your own insertion function or 
    just use method='multi' to tell pandas to pass multiple rows in a single INSERT query, which makes it a lot faster. 

"""



# Filter out warnings signs, they're just noise
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

#------------------------------------------------POTENTIALLY USEFUL
# Iteration over an array 
"""
list = [1, 3, 5, 7, 9]

# Using for loop
for i in list:
    print(i)
    # expected output: the numbers print out one at a time in sequential order

# Using for loop
array = ["Var1","Var2","Var3"]
for i in range(len(array)):
    print(array[i])

# Using while loop
list = [1, 3, 5, 7, 9]
# Getting length of list
length = len(list)
i = 0
# Iterating using while loop
while i < length:
    print(list[i])
    i += 1
    # expected output: the numbers print out one at a time in sequential order

"""


# Recordings -- looking at yesterday
"""
directory = "\\USFL04FSX08V\PCS_Recordings"
for filename in os.listdir(directory):
    if filename.endswith('.wav'):
        today = date.today()
        # print('Today is:', today)
        yesterday = today - timedelta(days = 1)
        # print('Yesterday was:', yesterday)
        timestamp = date.fromtimestamp(directory.stat().st_mtime) -- looking at date modified in the dir
        if yesterday == timestamp:
            print(os.path.join(directory, filename))

        # get last modified info
        # modify only yesterday's
        continue
    else:
        pass
"""

# Recordings -- doesn't matter the date, all files need to be transcribed
"""
directory = r"Z:\\"
# basename -- this is availble if i ever want to output the transcription as text files
basename = os.path.basename(directory)
print(basename)
Output_dir = 'J:\Contact Center Reporting\Misc\Project Dump\Transcribe + {basename}.txt'
basename = os.path.basename(directory)

"""

# Supported formats
"""
import soundfile as sf
sf.available_formats()
sf.available_subtypes(format=None)
"""

# Cheking formats and subtypes
"""
def check_format(format, subtype=None, endian=None):
    import soundfileas sf
    sf.check_format('WAV', 'PCM_24') True
    try:
        return bool(_format_int(format, subtype, endian))
    except (ValueError, TypeError):
        return False
"""

# Basename
"""
import os

directory = "\\USFL04FSX08V\PCS_Recordings"
basename = os.path.basename(directory)
for filename in os.listdir(directory):
    if filename.endswith('.wav'):
        print(basename)
"""

# Google free Speech to Text -- failed

"""
for filename in os.listdir(directory):
    if filename.endswith(".WAV"):

        r = sr.Recognizer()
        with sr.AudioFile(directory) as source:
            audio = r.listen(source)
        try: 
            s = r.recognize_google(audio)
            #print('Text: '+s) #---- leave as note
            #print('The script has been transcribed.')
            Working_df = Dummy_df.append({'TRANSCRIPTION': s}, ignore_index=True)  ##df.append({'col name':val}, ignore_index=True)
            print(Working_df)
        except Exception as e:
            print('Exception: '+str(e))
        continue
    else:
        pass


# ValueError: Audio file could not be read as PCM WAV, AIFF/AIFF-C, or Native FLAC; check if file is corrupted or in another format
"""


# Testing out the best methods to locate files in a file path
# os method
"""
def all_recordings():
    import os
    #directory = r"\\USFL04FSX08V\PCS_Recordings\Recordings" # UNC - can read
    #directory = r"Z:\\Recordings\\" # Z drive - can read
    #directory = r"Z:\Recordings\PCS153533855.wav" # specific - can read

    directory = r"\\USFL04FSX08V\PCS_Recordings\Recordings" 
    basename = os.path.basename(directory)
    print("The recordings in this path include: ")
    for filename in os.listdir(directory):
        if filename.lower().endswith((".wav")): # TypeError: endswith first arg must be bytes or a tuple of bytes, not str
            result = print(filename)
            return result
        else: 
            return print("No file")

all_recordings()
"""

# glob method
"""
def all_recordings():
    import glob
    import numpy as np
    import os

    #paths to consider:
        #directory = r"\\USFL04FSX08V\PCS_Recordings\Recordings" # UNC - can read
        #directory = r"Z:\\Recordings\\" # Z drive - can read
        #directory = r"Z:\Recordings\PCS153533855.wav" # specific - can read

    directory = r"\\USFL04FSX08V\PCS_Recordings\Recordings" 
    #basename = os.path.basename(directory)
    print("The recordings in this path include: ")

    for file in glob.iglob(f"{directory }/*", recursive = True):
        result = file
        # grab one file at a time 

    def one_at_a_time():
        recordings_list = []
        recordings_list.append(result)
        print(recordings_list)
        one_at_a_time()

all_recordings()
"""

#------------------------------------------------EXPERIMENT SUCCESS
"""
def all_notes():
    import glob
    import numpy as np
    import os

    #paths to consider:
        #directory = r"\\USFL04FSX08V\PCS_Recordings\Recordings" # UNC - can read
        #directory = r"Z:\\Recordings\\" # Z drive - can read
        #directory = r"Z:\Recordings\PCS153533855.wav" # specific - can read

    directory = r"C:\Users\ckraft\Documents\Notes" 
    basename = os.path.basename(directory)
    print("The notes in this path include: ")
    for file in glob.iglob(f"{directory }/*", recursive = True):
        result = file
        # Populate an array from result
        notes_list = []
        notes_list.append(result)
        #print(notes_list)
        # grab one file at a time

        def one_at_a_time():
            notes_list = []
            notes_list.append(result)
            print(notes_list_list)
            one_at_a_time()
        all_notes()
"""

#------------------------------------------------LOOPING METHOD OF CHOICE
"""
def all_recordings():
    import glob
    import numpy as np
    import os
        #paths to consider:
            #directory = r"\\USFL04FSX08V\PCS_Recordings\Recordings" # UNC - can read
            #directory = r"Z:\\Recordings\\" # Z drive - can read
            #directory = r"Z:\Recordings\PCS153533855.wav" # specific - can read
            #directory = \\usfl04fsg01v\postcallsurvey # where all the NEWER PCS audio recordings live

    directory = r"\\USFL04FSX08V\PCS_Recordings\Recordings" 
        #basename = os.path.basename(directory)
    print("The recordings in this path include: ")
    for file in glob.iglob(f"{directory }/*", recursive = True):
        result = file
        # grab one file at a time 
        recordings_list = []
        recordings_list.append(result)
        print(recordings_list)               
all_recordings()
"""
############################################################ Automation Task(s) ############################################################

def main():
    directory = r"\\USFL04FSX08V\PCS_Recordings\Recordings" 
    #basename = os.path.basename(directory)


    print("The recordings in this path include: ")
    for file in glob.iglob(f"{directory }/*", recursive = True):
        result = file
        # grab one file at a time 
        recordings_list = []
        recordings_list.append(result)
        print(recordings_list) 

#------------------------------------------------PARSING: EXPERIMENT SUCCESS
    """
    # method 1
    my_str = "test_program_will_this_work"
    print(my_str.partition('_')[-1])
    
    #method 2
    string = "claire.kraft"
    print(string[0:6])
    
    # method 3
    string = "PCS15353310189.wav"
    string[:string.index(".")]
    
    # mini testing 
    i = '\\\\USFL04FSX08V\\PCS_Recordings\\Recordings\\PCS15353310189.wav'
    basename_suffix = i.partition('\\Recordings\\')[-1]
    print(basename_suffix) #PCS15353310189.wav
    # expected output for basename_suffix:  PCS15353310189.wav
    basename = basename_suffix[:basename_suffix.index(".")]
    print(basename)
    # expected output for basename: PCS15353310189
    """

    for i in range(len(recordings_list)): #ref: lines 124-126
        try:
            one_audio = one_audio + i
            basename_suffix = i.partition('\\Recordings\\')[-1] # don't need the root path, just need file.extension
            basename = basename_suffix[:basename_suffix.index(".")]
            #load pre-trained model and tokenizer
            tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
            model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
            speech, rate = librosa.load(one_audio,sr = 16000)
            #load audiio file
            import IPython.display as display
            display.Audio(one_audio, autoplay = True)
            input_values = tokenizer(speech, return_tensors = 'pt').input_values
            input_values
            #store logits (non-normalized predictions)
            logits = model(input_values).logits
            logits
            #store predicted IDs
            predicted_ids = torch.argmax(logits, dim = -1)
            #decode the audio to generate text = book transcription
            transcription = tokenizer.decode(predicted_ids[0])
            print(transcription)
            
            # Appending data to Dummy_df
            Working_df = Dummy_df.append({'PCS_ID': basename,'TRANSCRIPTION': transcription, 'MODIFIED_DATETIME': now}, ignore_index = True)  ##df.append({'col name':val}, ignore_index=True)
            print(Working_df)
            # Inserting data into Oracle
            
            """
            Options for writing to SQL database:
            1. For a single line, write the "INSERT" sql.
            2. In bulk, write each line to a pandas dataframe, then use Pandas to write the dataframe to the SQL table. 
                # my_data_frame.to_sql(TableName, engine, chunksize=<yourParameterLimit>, method='multi')
                # here is a method parameter in pandas.to_sql() where you can define your own insertion function or 
                # just use method='multi' to tell pandas to pass multiple rows in a single INSERT query, which makes it a lot faster.                        
            """
            
            
            from sqlalchemy import create_engine, inspect              
            connstr  = "oracle://{}:{}@{}".format(SCHEMA, PASSWORD, DATABASE)
            conn     = sqlalchemy.create_engine(connstr)
            #df.to_sql("TableName", engine, schema="SchemaName", if_exists="append", index=False)
            Working_df.to_sql('pcs_transcriptions',conn, schema = 'OPS_REPORTING', if_exists = 'append', index = False)           
        except Exception as e:
            print('Exception: ' +str(e))
        continue 
    else:
        pass
if __name__== "__main__":
    main()

#------------------------------------------------NON LOOPING METHOD OF CHOICE
# Non looping--manually feed one file into line 425 at a time
""" 
#load pre-trained model and tokenizer
tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")
speech, rate = librosa.load("Z:\PCS15372311580.wav",sr=16000)
#load audiio file
import IPython.display as display
display.Audio("Z:\PCS15372311580.wav", autoplay=True)
input_values = tokenizer(speech, return_tensors = 'pt').input_values
input_values
#store logits (non-normalized predictions)
logits = model(input_values).logits
logits
#store predicted IDs
predicted_ids = torch.argmax(logits, dim =-1)
#decode the audio to generate text = book transcription
transcription = tokenizer.decode(predicted_ids[0])
print(transcription)

# Appending data to Dummy_df
Working_df = Dummy_df.append({'PCS_ID':0,'TRANSCRIPTION': transcription, 'MODIFIED_DATETIME': now}, ignore_index=True)  ##df.append({'col name':val}, ignore_index=True)
print(Working_df)

# For if transcription is written to a text file

text_file = open(r'J:\Contact Center Reporting\Misc\Project Dump\Transcribe\Test4_Script.txt','w')
text_file.write(transcription)
text_file.close()

# Inserting data into Oracle

### Options for writing to SQL database:
### 1. For a single line, write the "INSERT" sql.
### 2. In bulk, write each line to a pandas dataframe, then use Pandas to write the dataframe to the SQL table. 
    # my_data_frame.to_sql(TableName, engine, chunksize=<yourParameterLimit>, method='multi')
    # here is a method parameter in pandas.to_sql() where you can define your own insertion function or 
    # just use method='multi' to tell pandas to pass multiple rows in a single INSERT query, which makes it a lot faster.
    

from sqlalchemy import create_engine, inspect              
connstr  = "oracle://{}:{}@{}".format(SCHEMA, PASSWORD, DATABASE)
conn     = sqlalchemy.create_engine(connstr)


#df.to_sql("TableName", engine, schema="SchemaName", if_exists="append", index=False)
Working_df.to_sql('pcs_transcriptions',conn, schema = 'OPS_REPORTING', if_exists = 'append', index = False)
"""





