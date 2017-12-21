import lib
import os
import json
import argparse

dir = os.path.dirname(__file__)

positiveImageDirectory = os.path.join(dir, "./../img/positive")
negativeImageDirectory = os.path.join(dir, "./../img/negative")
testImageDirectory = os.path.join(dir, "./../img/test")
outFeatureDirectory = os.path.join(dir, "./../data")

config = json.load(open(os.path.join(dir, "config.json"), 'r'))

def generatePositiveTrainData():
    features = lib.getSourceLocations("Positive")
    lib.loadImages(features, config, positiveImageDirectory)

def generateNegativeTrainData():
    features = lib.getSourceLocations("Negative")
    lib.loadImages(features, config, negativeImageDirectory)

def generateTestData():
    features = lib.getSourceLocations("Test")
    lib.loadImages(features, config, testImageDirectory, testMode=True)

def generateAllTrainData():
    generatePositiveTrainData()
    generateNegativeTrainData()
    # getTestSample()

def test():
    features = lib.getSourceLocations("Test")
    lib.calculateSegmentScores(features, testImageDirectory, outFeatureDirectory)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task")
    args = parser.parse_args()
    if args.task == "getAllTrainData":
        generateAllTrainData()
    elif args.task == "negativeTrainData":
        generateNegativeTrainData()
    elif args.task == "positiveTrainData":
        generatePositiveTrainData()
    elif args.task == "testData":
        generateTestData()
    elif args.task == "train":
        raise NotImplementedError()
    elif args.task == "test":
        test()
    elif args.task == "route":
        raise NotImplementedError()
    else:
        raise ValueError("Unknown Task")
