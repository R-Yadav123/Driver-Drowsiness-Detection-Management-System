# This file will be used for the Machine Learning Image Classification Model for Driver Drowsiness Detection
# Training 
# This was developed with the assistance of artificial intelligence

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models



import json
from PIL import Image, UnidentifiedImageError
from torch.utils.data import Dataset, DataLoader
import os
import torch
from torchvision import transforms

# -------------------------
# Safer Drowsiness Dataset
# -------------------------
class DrowsinessDataset(Dataset):
    def __init__(self, images_folder, labels_file, transform=None):
        self.images_folder = images_folder
        self.transform = transform

        # Load JSON
        with open(labels_file, 'r') as f:
            data = json.load(f)

        self.image_labels = []
        skipped = 0
        for fname, boxes in data["boundingBoxes"].items():
            img_path = os.path.join(images_folder, fname)
            if not os.path.isfile(img_path):
                skipped += 1
                continue
            try:
                # quick check if image can be opened
                img = Image.open(img_path).convert("RGB")
                img.close()
            except UnidentifiedImageError:
                skipped += 1
                continue

            # Assign label: if any box is "mata_terpejam" -> drowsy (1), else alert (0)
            label = 1 if any(box["label"] == "mata_terpejam" for box in boxes) else 0
            self.image_labels.append((fname, label))

        print(f"Loaded {len(self.image_labels)} images from {images_folder}")
        if skipped > 0:
            print(f"Skipped {skipped} missing or corrupted images.")

        self.classes = {0: "alert", 1: "drowsy"}
        if len(self.image_labels) == 0:
            raise ValueError("No valid images found in folder!")

    def __len__(self):
        return len(self.image_labels)

    def __getitem__(self, idx):
        fname, label = self.image_labels[idx]
        img_path = os.path.join(self.images_folder, fname)
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, label

# -------------------------
# Data transforms
# -------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# -------------------------
# Load datasets and test DataLoader
# -------------------------
train_dataset = DrowsinessDataset("training", "training/bounding_boxes.labels", transform=transform)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

# Test iteration to catch issues early
print("Testing DataLoader...")
for i, (images, labels) in enumerate(train_loader):
    print(f"Batch {i}: images {images.shape}, labels {labels}")
    if i >= 1:  # only first batch
        break
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from tqdm import tqdm  # nice progress bar

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# Load pre-trained MobileNetV2
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
model.classifier[1] = nn.Linear(1280, 2)  # two classes: alert, drowsy
model = model.to(device)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 5

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0

    # tqdm progress bar for batches
    for batch_idx, (images, labels) in enumerate(tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs}")):
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

        # Print batch loss every 5 batches
        if batch_idx % 5 == 0:
            print(f"Batch {batch_idx}, Loss: {loss.item():.4f}")

    print(f"Epoch {epoch+1} completed, Average Loss: {running_loss/len(train_loader):.4f}")

# Save the trained model
torch.save(model.state_dict(), "drowsiness_model.pth")
print("Model saved as drowsiness_model.pth")
