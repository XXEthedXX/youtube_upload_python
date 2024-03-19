import httplib2
import os
import random
import sys
import time
import argparse

# Make sure client_secrets.json is in the same file or it messes up everything!
import json
from oauthlib.oauth2 import DeviceClient

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload


# Tell http not to retry and handle it ourselves
httplib2.RETRIES = 1

# Retry a max of 5 times
MAX_RETRIES = 5

# Always retry these exceptions
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
# Always retry when apiclient.errors.HttpError hits these codes
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# Let MY_CLIENT_SECRETS hold client_secrets.json data
# In otherwords, the OAuth 2.0 data (client_id, client_secret)
MY_CLIENT_SECRETS = "client_secrets.json"

# Some needed? variables for YouTube and it's scopes
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Craft a message if MISSING_MY_CLIENT_SECRETS
MISSING_MY_CLIENT_SECRETS = """
WARNING: Please configure OAuth 2.0

You are currently missing the client_secrets file,
I believe it should be located here: %s
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), MY_CLIENT_SECRETS))
# The % concatenates the client secrets

POSSIBLE_PRIVACY_STATUSES = ("public", "private", "unlisted")

# create a function to get_authenticated
# TODO: Create a flow
# TODO: Create a storage (for credentials)
# TODO: "Create" credentials (and store in storage)
# Example usage - answer to wtf am I returning
# request_body = lets_get_authenticated()
# print(request_body)
def lets_get_authenticated(theArg):
    # GPT & docs - DeviceClient is a function that takes in client_id
    # GPT - the grant type is implicitly included

    # Grab secret client info by checking client_secrets.json
    with open('client_secrets.json') as secrets:
        unraveled_secrets = json.load(secrets)

    # Grab credentials
    client_id = unraveled_secrets['installed']['client_id']
    client_secret = unraveled_secrets['installed']['client_secret']

    # Create a representation of the client and perform a request to make a URI
    my_client = DeviceClient(client_id)
    request_body = my_client.prepare_request_body(scope=[YOUTUBE_UPLOAD_SCOPE])

    return request_body

# create a function to begin_upload
def begin_upload(youtube, options):
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body=dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )
    # above sets up the given arguments for youtube

    # below calls API videos.insert method to create and upload videos
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        # The chunksize parameter specifies the size of each chunk of data, in
        # bytes, that will be uploaded at a time. Set a higher value for
        # reliable connections as fewer chunks lead to faster uploads. Set a lower
        # value for better recovery on less reliable connections.
        #
        # Setting "chunksize" equal to -1 in the code below means that the entire
        # file will be uploaded in a single HTTP request. (If the upload fails,
        # it will still be retried where it left off.) This is usually a best
        # practice, but if you're using Python older than 2.6 or if you're
        # running on App Engine, you should set the chunksize to something like
        # 1024 * 1024 (1 megabyte).
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    # If can get working, make it so that the resume_upload function works

# create a function to resume_upload
def resume_upload():
    broke = "it broke!"
    return broke

# create a main function to call it all together
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Video file to upload")
    parser.add_argument("--title", help="Video title", default="Test Title")
    parser.add_argument("--description", help="Video description",
                           default="Test Description")
    parser.add_argument("--category", default="22", help="Numeric video category. " + "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    parser.add_argument("--keywords", help="Video keywords, comma separated", default="")
    parser.add_argument("--privacyStatus", choices=POSSIBLE_PRIVACY_STATUSES[0], default=POSSIBLE_PRIVACY_STATUSES[0], help="Video privacy status.")
    theArgument = parser.parse_args()

    if not os.path.exists(theArgument.file):
        exit("Please choose an actual, existing file using --file buddy...")

    youtube = lets_get_authenticated(theArgument) # youtube now equals our request url for credentials?

    try:
        begin_upload(youtube, theArgument)
    except:
        print("Shoot, we got some sort of error here...")
        print(sys.exc_info()[0])