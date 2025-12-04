# This file will be used for the Machine Learning Image Classification Model for Driver Drowsiness Detection
# Testing 
# This was developed with the assistance of artificial intelligence

import torch
import torch.nn as nn
from torchvision import models, transforms
from torch.utils.data import DataLoader
from Training import DrowsinessDataset  # or from Training import DrowsinessDataset

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# Define the same transforms used in training
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

# Load testing dataset
test_dataset = DrowsinessDataset("testing", "testing/bounding_boxes.labels", transform=transform)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
print(f"Loaded {len(test_dataset)} images from testing")

# Load trained model
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
model.classifier[1] = nn.Linear(1280, 2)  # match number of classes
model.load_state_dict(torch.load("drowsiness_model.pth", map_location=device))
model = model.to(device)
model.eval()

# Testing loop
correct = 0
total = 0

with torch.no_grad():
    for batch_idx, (images, labels) in enumerate(test_loader):
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        print(f"Batch {batch_idx}, Batch Accuracy: {(predicted == labels).sum().item() / labels.size(0) * 100:.2f}%")

# Final accuracy
accuracy = 100 * correct / total
print(f"Final Testing Accuracy: {accuracy:.2f}%")
