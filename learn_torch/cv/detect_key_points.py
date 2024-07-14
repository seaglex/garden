import torchvision
import torchvision.transforms.functional as F
import os
import os.path
import numpy as np
import json
from PIL import Image
import copy


class ImgDataset(object):
    def __init__(self, path):
        fnames = os.listdir(path)
        fnames = [fname for fname in fnames if fname.split('.')[-1] in ("png", "jepg", "jpg")]
        self.image_fnames = [os.path.join(path, fname) for fname in fnames]

    def __len__(self):
        return len(self.image_fnames)

    def __getitem__(self, item):
        img = Image.open(self.image_fnames[item]).convert("RGB")
        return F.to_tensor(img)


def detect_key_points():
    path = "/Users/weixuan/code/frontier/pifuhd/sample_images/"
    model = torchvision.models.detection.keypointrcnn_resnet50_fpn(True)
    model.eval()

    template = {"version": 1.3, "people": []}
    person = {"person_id": [-1], "pose_keypoints_2d": [], "face_keypoints_2d": [], "hand_left_keypoints_2d": [],
         "hand_right_keypoints_2d": [], "pose_keypoints_3d": [], "face_keypoints_3d": [], "hand_left_keypoints_3d": [],
         "hand_right_keypoints_3d": []}
    fnames = os.listdir(path)
    for fname in fnames:
        if fname.split(".")[-1] not in ("png", "jpeg", "jpg"):
            continue
        print(fname)
        rect_fname = ".".join(fname.split(".")[:-1]) + "_rect.txt"
        keypoint_fname = ".".join(fname.split(".")[:-1]) + "_keypoints.json"
        img = Image.open(os.path.join(path, fname)).convert("RGB")
        img_data = torchvision.transforms.functional.to_tensor(img)
        result = model([img_data])
        np.savetxt(os.path.join(path, rect_fname), result[0]["boxes"].detach().numpy())
        with open(os.path.join(path, keypoint_fname), "w") as fout:
            template["people"] = []
            num_people = result[0]["keypoints"].shape[0]
            for n in range(num_people):
                p = copy.deepcopy(person)
                p["pose_keypoints_2d"] = [float(x) for x in result[0]["keypoints"][0].reshape(-1).detach().numpy()]
                template["people"].append(p)
            json.dump(template, fout)
