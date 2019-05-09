''' A script that reads text from a file and uploads to Amazon Polly
    Amazon Polly allows text to be turned into audio, an mp3 file
    is created and uploaded to an s3 buckets
'''

import boto3
import sys
import datetime
from contextlib import closing

BUCKET_NAME = "support-ops-dublin"

POLLY_CLIENT = boto3.client('polly')
S3_CLIENT = boto3.client('s3')
CURRENT_DATETIME = datetime.datetime.now().strftime('%d-%m-%y %H:%M:%S')

def check_args():
    if len(sys.argv) > 1 :
        text_file = sys.argv[1]
        file=open(text_file, "r")
        call_polly(file)
    else:
        print("No text file specified!")

def call_polly(file):
    if file.mode == 'r':
        contents = file.read()
        try:
            response = POLLY_CLIENT.synthesize_speech(
        	    OutputFormat='mp3',
        	    Text=contents,
        	    TextType='text',
        	    VoiceId='Salli'
    	    )
        except Exception as e:
            print(e)
        upload_to_s3(file,response)

def upload_to_s3(file, response):
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = "polly-boto.mp3"
            s3_file_name = "PollyAudio_" + str(CURRENT_DATETIME)
            try:
                # Open a file for writing the output as a binary stream
                with open(output, "wb") as file:
                    file.write(stream.read())
                    S3_CLIENT.upload_file(output, BUCKET_NAME, 'AarronTest/{}'.format(s3_file_name))
            except IOError as ioe:
                # Could not write to file, exit gracefully
                print(ioe)
                sys.exit(-1)

def main():
    check_args()

if __name__ == "__main__":
    main()
