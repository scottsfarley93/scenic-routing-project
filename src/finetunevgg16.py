import keras
from keras.layers import *
import scipy
import sklearn
import numpy as np
import pandas as pd
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.optimizers import Adam
import os
from vgg16 import Vgg16

def vgg_ft(out_dim):
    vgg = Vgg16()
    vgg.ft(out_dim)
    model = vgg.model
    return model


DATA_DIR = os.path.join(os.path.dirname(__file__), './../img')

X_dim = 224
Y_dim = 224


datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True)

train_generator = datagen.flow_from_directory(
        DATA_DIR,
        target_size=(X_dim, Y_dim),
        batch_size=32,
        class_mode='binary')

valgen = ImageDataGenerator()

validation_generator = valgen.flow_from_directory(
        DATA_DIR,
        target_size=(X_dim, Y_dim),
        batch_size=32,
        class_mode='binary')


model = vgg_ft(1)

model.compile(optimizer=Adam(lr=0.001),
                loss='binary_crossentropy', metrics=['accuracy'])

print model.summary()

model.fit_generator(train_generator,steps_per_epoch=550, epochs=5, validation_data=validation_generator, validation_steps=10)

model.save(filepath="./scenic_model.h5")
