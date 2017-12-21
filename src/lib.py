import json
import geojson
import shapely
import shapely.geometry
import random
import requests
from ratelimit import rate_limited
import urllib
import os
import skimage
from skimage import io
from skimage import transform
import numpy
import keras
from keras.layers import *
import scipy
import sklearn
import numpy as np
import pandas as pd
from keras.preprocessing.image import ImageDataGenerator
from keras.preprocessing import image
from keras.models import Sequential
from keras.optimizers import Adam
import matplotlib.pyplot as plt
from scipy.misc import imread, imresize

fillerMean = 0.5

X_dim = 100
Y_dim = 100




dir = os.path.dirname(__file__)

def readGeojson(f):
    """Read a geojson file from disk"""
    geo = geojson.load(open(f, 'r'));
    return geo


def randomPointsOnLine(feature, numPoints):
    """Generate random points on a geojson line feature"""
    points = []
    linestring = shapely.geometry.LineString(feature.geometry.coordinates)
    length = linestring.length
    i = 0
    while i < numPoints:
        dist = random.uniform(0, length)
        point = linestring.interpolate(dist)
        points.append(point)
        i += 1
    return points

# @rate_limited(25)
def searchStreetLevelImages(latitude, longitude, apiToken, maxImages=5):
    """Return a list of Mapillary image keys"""
    if not apiToken:
        raise ValueError("API request must have a token")
    url = "https://a.mapillary.com/v3/images?client_id=%s&closeto=%s,%s"%(apiToken, longitude, latitude)
    call = requests.get(url)
    response = call.json()
    imgKeys = []
    if response['features']:
        i = 1
        for feature in response['features']:
            if i > maxImages:
                break
            key = feature['properties']['key']
            imgKeys.append(key)
            i += 1
    return imgKeys

# @rate_limited(25)
def downloadImage(url, target):
    """Download an image from url and save it to the target file"""
    urllib.urlretrieve(url, target)
    print "\t\tDownloaded image file from %s" % (url)

def downloadStreetLevelImages(imgKeys, targetDir, thumbSize=640, targetBasename=None):
    """Download the mapillary images and save them to disk"""
    idx = 0
    for key in imgKeys:
        if targetBasename is None:
            targetFile =  os.path.join(targetDir, key + ".jpg")
        else:
            targetFile = os.path.join(targetDir, str(targetBasename) + "_" + str(idx) + ".jpg")
        imageURL = "https://d1cuyjsrcm0gby.cloudfront.net/%s/thumb-%s.jpg" % (key, thumbSize)
        downloadImage(imageURL, targetFile)
        idx = idx + 1


## generate random points along the positive and negative example features
def loadImages(features, config, targetDir, testMode=False):
    ## features is a featureCollection
    j = 1
    for feature in features['features'][133:]:
        try:
            print "Processing segment: %s/%s" % (j, len(features['features']))
            segmentPoints = randomPointsOnLine(feature, config['pointsPerSegment'])
            i = 1
            for point in segmentPoints:
                coords = list(point.coords)
                imgTokens = searchStreetLevelImages(coords[0][1], coords[0][0], config['MapillaryToken'], config['maxImagesPerPoint'])
                if testMode:
                    targetBasename = feature['properties']['LINEARID']
                else:
                    targetBasename = None
                downloadStreetLevelImages(imgTokens,targetDir, targetBasename=targetBasename)
                print "\tFinished point %s of %s" % (i, config['pointsPerSegment'])
                i += 1
        except Exception as e:
            print str(e)
        j += 1

def calculateSegmentScores(features, testDir, outDir):
    dirList = os.listdir(testDir)
    theModel = loadModel(os.path.join(dir, "scenic_model_3.h5"))
    outFeaturesFile = open(os.path.join(outDir, "scenic_graph.json"), 'w')
    for feature in features['features']:
        featureID = feature['properties']['LINEARID']
        segImgs = getImagesForSegment(dirList, featureID)
        batch = numpy.zeros((len(segImgs), 100, 100, 3))
        idx = 0
        for i in segImgs:
            path = os.path.join(dir, testDir, i)
            batch[idx] = readImg(path)
            idx += 1
        segmentScores = predict(theModel, batch)
        if len(segmentScores) == 0:
            segmentScores = [fillerMean] * 10
        feature['properties']['rawScores'] = segmentScores
        feature['properties']['meanScore'] = float(numpy.mean(segmentScores))
        feature['properties']['meanScoreInv'] = float(1 - numpy.mean(segmentScores))
        feature['properties']['scoreVariance'] = float(numpy.var(segmentScores))
        feature['properties']['scoreCount'] = idx
        outFeaturesFile.write(json.dumps(feature) + "\n")
        print "%s: %s" % (feature['properties']['FULLNAME'], feature['properties']['meanScore'])


def getImagesForSegment(dirList, segmentID):
    segsImgs = []
    for path in dirList:
        if segmentID in path:
            segsImgs.append(path)
    return segsImgs

def readImg(imgPath, shape=(100, 100, 3)):
    img = imread(imgPath)
    rs = imresize(img, shape)
    return rs

def loadModel(weightsFile):
    model = Sequential()
    model.add(Conv2D(50, 3, activation='relu', padding='same', input_shape=(X_dim, Y_dim, 3)))
    model.add(BatchNormalization(axis=1))
    model.add(MaxPooling2D())
    model.add(Conv2D(50, 3, activation='relu', padding='same'))
    model.add(BatchNormalization(axis=1))
    model.add(MaxPooling2D())
    model.add(Conv2D(50, 3, activation='relu', padding='same'))
    model.add(BatchNormalization(axis=1))
    model.add(MaxPooling2D())
    model.add(Conv2D(50, 3, activation='relu', padding='same'))
    model.add(BatchNormalization(axis=1))
    model.add(MaxPooling2D())
    model.add(Conv2D(50, 3, activation='relu', padding='same'))
    model.add(BatchNormalization(axis=1))
    model.add(MaxPooling2D())
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer=Adam(lr=0.001),
                    loss='binary_crossentropy', metrics=['accuracy'])
    model.load_weights(weightsFile)
    return model

def predict(model, batch):
    preds = model.predict(batch)
    preds = [float(item) for p in preds for item in p]
    return preds





def getSourceLocations(label):
    """Read in the geojson locations of road segements for a given feature"""
    if label == "Positive":
        return readGeojson(os.path.join(dir, "./../data/CA_scenic.geojson"))
    elif label == "Negative":
        return readGeojson(os.path.join(dir, "./../data/interstates.geojson"))
    elif label == "Test":
        return readGeojson(os.path.join(dir, "./../data/ps_roads_ca.geojson"))
    else:
        raise ValueError("Unknown source label")
