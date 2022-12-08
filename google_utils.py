import requests
import io
import os
from googlesearch import search
import tldextract

# Imports the Google Cloud client library
from google.cloud import vision

def detect_logos_uri(uri):
    """Detects logos in the file located in Google Cloud Storage or on the Web.
    """
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.logo_detection(image=image)
    logos = response.logo_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return [logo.description for logo in logos]

def detect_logos_filepath(path):
    """Detects logos in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.logo_detection(image=image)
    logos = response.logo_annotations

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return [logo.description for logo in logos]


def reduceURL(url):
    return tldextract.extract(url)

def getGoogleResultFromKeyword(keyword):
    return list(search(keyword, tld="com", num=1, stop=1, pause=2))

if __name__ == "__main__":
    fishingresults = getGoogleResultFromKeyword("fishing")
    # reducedResults = [reduceURL(result) for result in fishingresults]
    # print(reducedResults)
    print(fishingresults)




