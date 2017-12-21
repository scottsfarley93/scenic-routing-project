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


DATA_DIR = os.path.join(os.path.dirname(__file__), './../img')

X_dim = 75
Y_dim = 75


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
model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dense(256, activation='relu'))
model.add(Dense(1, activation='sigmoid'))


model.compile(optimizer=Adam(lr=0.001),
                loss='binary_crossentropy', metrics=['accuracy'])

print model.summary()

model.fit_generator(train_generator,steps_per_epoch=550, epochs=5, validation_data=validation_generator, validation_steps=10)

model.save(filepath="./scenic_model.h5")
