import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Define a simple sequential model
model = Sequential([
    Dense(64, activation='relu', input_shape=(784,)),
    Dense(64, activation='relu'),
    Dense(10, activation='softmax')
])

# Compile the model
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Generate some dummy data
import numpy as np
data = np.random.random((1000, 784))
labels = np.random.randint(10, size=(1000,))

# Train the model (you might use your own data here)
model.fit(data, labels, epochs=10)

# Save the model to an .h5 file
model.save("sample_model.h5")
