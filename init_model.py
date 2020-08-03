#!/usr/bin/env python3

# If Fast R-CNN model is not available - it will be downloaded 

import torchvision

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

model_ft = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
