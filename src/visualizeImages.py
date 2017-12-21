from scipy import misc
from scipy import ndimage
import os
dir = os.path.dirname(__file__)
import matplotlib.image as mpimg
import random
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import numpy as np
from skimage.transform import resize


# Scale and visualize the embedding vectors
def plot_embedding(X, title=None):
    x_min, x_max = np.min(X, 0), np.max(X, 0)
    X = (X - x_min) / (x_max - x_min)

    plt.figure()
    ax = plt.subplot(111)
    # for i in range(X.shape[0]):
    #     plt.text(X[i, 0], X[i, 1], str(digits.target[i]),
    #              color=plt.cm.Set1(y[i] / 10.),
    #              fontdict={'weight': 'bold', 'size': 9})

    if hasattr(offsetbox, 'AnnotationBbox'):
        # only print thumbnails with matplotlib > 1.0
        shown_images = np.array([[1., 1.]])  # just something big
        for i in range(digits.data.shape[0]):
            dist = np.sum((X[i] - shown_images) ** 2, 1)
            if np.min(dist) < 4e-3:
                # don't show points that are too close
                continue
            shown_images = np.r_[shown_images, [X[i]]]
            imagebox = offsetbox.AnnotationBbox(
                offsetbox.OffsetImage(digits.images[i], cmap=plt.cm.gray_r),
                X[i])
            ax.add_artist(imagebox)
    plt.xticks([]), plt.yticks([])
    if title is not None:
        plt.title(title)

def plotRandomImages(targetDir, numImg):
    l = os.listdir(targetDir)
    random.shuffle(l)
    toPlot = l[:numImg]
    fig = plt.figure()
    idx = 1
    for img in toPlot:
        a=fig.add_subplot(1,numImg,idx)
        imgplot = plt.imshow(mpimg.imread(os.path.join(targetDir, img)))
        idx += 1
    plt.show()

def readImage(imagePath):
     return misc.imread(path)


def readImageAsArray(pathToImage):
    img = misc.imread(pathToImage)
    resized = resize(img, (128, 128), mode='reflect')
    flat = resized.flatten()
    return flat

def tsne(loadFirst = False):
    if loadFirst:
        targetDir = os.path.join(dir, "./../img/positive/")
        targets = np.zeros(shape=(1000,128*128*3))
        labels = []
        i = 0
        dirList = os.listdir(targetDir)
        random.shuffle(dirList)
        for image in dirList[:500]:
            try:
                path = os.path.join(targetDir, image)
                imgData = readImageAsArray(path)
                targets[i] = imgData
                i += 1
                if i % 100 == 0:
                    print i
                labels.append("green")
            except Exception as e:
                print e
        targetDir = os.path.join(dir, "./../img/negative/")
        i = 0
        dirList = os.listdir(targetDir)
        random.shuffle(dirList)
        for image in dirList[:500]:
            try:
                path = os.path.join(targetDir, image)
                imgData = readImageAsArray(path)
                targets[i] = imgData
                i += 1
                if i % 100 == 0:
                    print i
                labels.append("red")
            except Exception as e:
                print e
        np.save(open("data.npy", 'w'), targets)
    else:
        targets= np.load(open("negativeData.npy", 'r'))
        labels = ["green"] * 500 + ['red'] * 500
    X_embedded = TSNE(n_components=2, verbose=True, learning_rate=10, n_iter=2000, perplexity=100, init='pca').fit_transform(targets)
    plt.scatter(X_embedded[:, 0],X_embedded[:, 1], c=labels)
    # plot_embedding(X_embedded)
    plt.show()

print tsne(loadFirst = False)
