import random
import sys

import numpy as np
import pandas as pd
import torch
from PIL import Image
from skimage import io, transform
from torch.utils.data import DataLoader, Dataset


class face_dataset(Dataset):
    def __init__(self, csv_file, transform=None):
        self.data_path_details = pd.read_csv(csv_file, header=None)
        self.transform = transform

    def __len__(self):
        return len(self.data_path_details)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_path = self.data_path_details.iloc[idx, 0]
        img_path = img_path.replace(
            "/home/DSO_SSD/Deepfake_data/FF++/faces/",
            "/home/kcq/FF++_faces_masks_labels/faces_224/",
        )
        img = io.imread(img_path)
        label = self.data_path_details.iloc[idx, 1]

        sample = {"face": img, "label": label}

        if self.transform:
            sample = self.transform(sample)
        return sample


class my_transforms(object):
    """
    normalize = transforms.Normalize(mean=[0.5, 0.5, 0.5],
                                  std=[0.5, 0.5, 0.5])
    """

    # def __init__(self, output_size=None, RandomHorizontalFlip=False, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    def __init__(self, output_size=None, RandomHorizontalFlip=False, mean=0.5, std=0.5):
        assert isinstance(output_size, (int, tuple))
        if isinstance(output_size, int):
            self.output_size = (output_size, output_size)
        else:
            assert len(output_size) == 2
            self.output_size = output_size

        self.RandomHorizontalFlip = RandomHorizontalFlip
        self.mean = mean
        self.std = std

    def __call__(self, sample):
        img_ori = sample["face"]
        label = sample["label"]
        ### resize
        img = transform.resize(img_ori, self.output_size)

        ### random horizontal flip
        if self.RandomHorizontalFlip and random.random() < 0.5:
            img = img[:, ::-1, :]

        ### (h, w, c) -> (c, h, w)
        img = img.transpose(2, 0, 1)

        ### to pytorch tensor
        img = torch.from_numpy(img.copy()).float()
        label = torch.tensor(label).long()
        # print('label:', label)

        ### normalize
        img = (img - self.mean) / self.std

        ### output
        sample = {"faces": img, "labels": label}
        return sample
