from typing import List
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms

from PIL import Image

import os


class FeaturesExtractor(nn.Module):
    def __init__(self):
        super(FeaturesExtractor, self).__init__()
        # load pretrained model
        self.model = models.resnet50(pretrained=True)
        # prepare data transforms
        self.transform = transforms.Compose([
            # PIL Image to PyTorch tensor
            transforms.ToTensor(),
            # resize and normalize for ResNet
            transforms.Resize(size=(224, 224)),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225])
        ])
        # replace fc head and return results from previous layer (avgpool)
        self.model.fc = nn.Sequential()
        # set model to evaluation mode
        self.model.eval()

    def forward(self, x):
        x = self.model(x)
        return x


class SimilarityDataset(torch.utils.data.Dataset):
    def __init__(self, base_path: str, image_paths: List[str], transform: transforms.Compose=None):
        self.base_path = base_path
        self.image_paths = image_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx: int):
        img_path = self.image_paths[idx]
        img_path = os.path.join(self.base_path, img_path)
        image = Image.open(img_path)
        # apply data preprocessing transforms if available
        if self.transform:
            image = self.transform(image)
        return image

