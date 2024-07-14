from PIL import Image
import torchvision.transforms.functional
import json
import numpy as np
import os.path
import torch


def add_points(img_data, points):
    for x, y, c in points:
        x, y = int(x), int(y)
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                img_data[:, j, i] = 0
    return


def process_key_points(image_name):
    name, _ = os.path.splitext(image_name)
    boy_img = Image.open(image_name)
    boy_data = torchvision.transforms.functional.to_tensor(boy_img)
    with open(name + "_keypoints.json", "r") as fin:
        boy_key_points = json.load(fin)
    add_points(boy_data, np.array(boy_key_points["people"][0]["pose_keypoints_2d"]).reshape(-1, 3))
    torchvision.transforms.functional.to_pil_image(boy_data).save(name + "_keypoints.png")


def process_rect(image_name, is_delta=False):
    name, _ = os.path.splitext(image_name)
    boy_img = Image.open(image_name)
    boy_data = torchvision.transforms.functional.to_tensor(boy_img)
    boy_rect = np.loadtxt(name + "_rect.txt")
    boy_rect = boy_rect.reshape(-1, 4)
    shape = boy_data.shape[1:]
    for x, y, x_max, y_max in boy_rect:
        x, y = int(np.round(x)), int(np.round(y))
        if is_delta:
            x_max, y_max = int(np.round(x_max)), int(np.round(y_max))
        else:
            x_max, y_max = int(np.round(x + x_max)), int(np.round(y + y_max))
        for i in range(max(x, 0), min(x_max + 1, shape[1])):
            if 0 <= y < shape[0]:
                boy_data[:, y, i] = 0
            if 0 <= y_max < shape[0]:
                boy_data[:, y_max, i] = 0
        for j in range(max(y, 0), min(y_max + 1, shape[0])):
            if 0 <= x < shape[1]:
                boy_data[:, j, x] = 0
            if 0 <= x_max < shape[1]:
                boy_data[:, j, x_max] = 0
    torchvision.transforms.functional.to_pil_image(boy_data).save(name + "_rect.png")


def resize_image(image_name, width=512, height=512):
    name, _ = os.path.splitext(image_name)
    src_img = Image.open(image_name)
    src = torchvision.transforms.functional.to_tensor(src_img)
    l_size = max(src.shape[1:])
    dst = torch.zeros(*src.shape[:1], l_size, l_size)
    dst[:, 0:src.shape[1], 0:src.shape[2]] = src
    torchvision.transforms.functional.to_pil_image(dst).resize((width, height)).save(name + "_rs.png")
