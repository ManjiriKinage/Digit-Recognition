import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks

def load_and_preprocess_data():
    """Load MNIST dataset, normalize pixel values to [0, 1], and reshape for CNN input."""
    print("[INFO] Loading MNIST dataset...")
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
    
    print(f"   Training samples: {x_train.shape[0]}, Test samples: {x_test.shape[0]}")
    print(f"   Original image dimensions: {x_train.shape[1:]}")
    
    # Normalize pixel values from [0, 255] to [0.0, 1.0]
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0
    
    # Reshape from (N, 28, 28) to (N, 28, 28, 1) for grayscale CNN channel
    x_train = np.expand_dims(x_train, -1)
    x_test = np.expand_dims(x_test, -1)
    
    print(f"   Processed shape: {x_train.shape}")
    return (x_train, y_train), (x_test, y_test)

def build_cnn_model():
    """Construct a high-performance Convolutional Neural Network for digit classification."""
    print("[INFO] Building CNN Architecture...")
    model = models.Sequential([
        # Block 1
        layers.Input(shape=(28, 28, 1)),
        layers.Conv2D(32, kernel_size=(3, 3), activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(64, kernel_size=(3, 3), activation="relu", padding="same"),
        layers.BatchNormalization(),
        layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
        layers.BatchNormalization(),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Dropout(0.25),
        
        # Classification Head
        layers.Flatten(),
        layers.Dense(256, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(10, activation="softmax")
    ])
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    model.summary()
    return model

def plot_training_history(history, save_path="training_history.png"):
    """Plot and save training/validation accuracy and loss curves."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy Plot
    ax1.plot(history.history["accuracy"], label="Training Accuracy", color="#6366f1", linewidth=2)
    ax1.plot(history.history["val_accuracy"], label="Validation Accuracy", color="#10b981", linewidth=2)
    ax1.set_title("Model Accuracy over Epochs", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Epoch", fontsize=12)
    ax1.set_ylabel("Accuracy", fontsize=12)
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="lower right")
    
    # Loss Plot
    ax2.plot(history.history["loss"], label="Training Loss", color="#f43f5e", linewidth=2)
    ax2.plot(history.history["val_loss"], label="Validation Loss", color="#f59e0b", linewidth=2)
    ax2.set_title("Model Loss over Epochs", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Epoch", fontsize=12)
    ax2.set_ylabel("Loss", fontsize=12)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="upper right")
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[INFO] Training curves saved to {save_path}")

def plot_confusion_matrix(y_true, y_pred, save_path="confusion_matrix.png"):
    """Compute and save confusion matrix heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=True,
                xticklabels=range(10), yticklabels=range(10),
                linewidths=0.5, linecolor="#e2e8f0")
    plt.title("Confusion Matrix on 10,000 MNIST Test Set", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("Predicted Digit", fontsize=12, labelpad=10)
    plt.ylabel("True Digit", fontsize=12, labelpad=10)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"[INFO] Confusion matrix saved to {save_path}")

def main():
    (x_train, y_train), (x_test, y_test) = load_and_preprocess_data()
    model = build_cnn_model()
    
    callbacks_list = [
        callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=3,
            restore_best_weights=True,
            verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=2,
            min_lr=1e-5,
            verbose=1
        )
    ]
    
    epochs = 10
    batch_size = 128
    print(f"\n[INFO] Training CNN model for up to {epochs} epochs (Batch Size: {batch_size})...")
    
    history = model.fit(
        x_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=0.1,
        callbacks=callbacks_list,
        verbose=1
    )
    
    print("\n[INFO] Evaluating model on 10,000 unseen test images...")
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"   Test Loss    : {test_loss:.4f}")
    print(f"   Test Accuracy: {test_acc * 100:.2f}%")
    
    # Save model
    model_path = "digit_model.keras"
    model.save(model_path)
    print(f"\n[INFO] Model successfully saved to: {model_path}")
    
    # Generate Visualizations
    plot_training_history(history)
    
    print("[INFO] Generating predictions for confusion matrix...")
    y_pred_probs = model.predict(x_test, verbose=0)
    y_pred = np.argmax(y_pred_probs, axis=1)
    
    plot_confusion_matrix(y_test, y_pred)
    
    print("\n[INFO] Classification Report:")
    print(classification_report(y_test, y_pred, digits=4))

if __name__ == "__main__":
    main()

