import json
import pickle
import socket
from pathlib import Path

import numpy as np
import tqdm


def load_images(
    datasets={"ADNI2", "ADNI2-2", "PPMI", "4RTNI", "TrackHD"},
    classes={
        "CN",
        "AD",
        "MCI",
        "EMCI",
        "LMCI",
        "SMC",
        "Control",
        "PD",
        "SWEDD",
        "Prodromal",
        "PSP",
        "CBD",
        "Oth" "control_subject",
        "early_hd",
        "premanifest_gene_carrier",
    },
    size="full",
    unique=True,
    blacklist=True,
    dryrun=False,
):
    """
    Args:
        datasets (set[str]): dataset kinds
        classes (set[str]): class labels
        size (str): either 'full' or 'half'
        unique (bool): if True, only one scan per subject
        blacklist (bool): if True, failed scans are excluded
        dryrun (bool): if True, do not load image from the disk
    Returns:
        list[dict]
    """

    root_dir = Path("/data" if socket.gethostname().startswith("plant-ai") else "/home")

    if size == "full" and root_dir == Path("/home"):
        raise NotImplementedError("full-size images are not available on lab servers (yet).")

    # all_subjects = json.loads((root_dir / Path("radiology_datas/pei/all_subjects.json")).read_text())
    all_subjects = json.loads((Path("all_subject.json")).read_text())
    matching_images = []

    for subject in all_subjects:
        if subject["dataset"] not in datasets:
            continue
        if subject["class"] not in classes:
            continue
        for image in subject["images"]:
            if image["blacklisted"] and blacklist:
                continue
            image["subject_id"] = subject["id"]
            image["class"] = subject["class"]
            image["dataset"] = subject["dataset"]
            matching_images.append(image)
            if unique:
                break

    if not dryrun:

        image_loaders = {
            ".pkl": lambda pkl_path: pickle.loads(pkl_path.read_bytes()),
            ".npy": lambda npy_path: np.load(npy_path),
        }

        for image in tqdm.tqdm(matching_images):
            if size == "half":
                img_path = root_dir / Path(image["halfsize_img_path"])
            if size == "full":
                img_path = root_dir / Path(image["fullsize_img_path"])
            image["voxel"] = image_loaders[img_path.suffix](img_path)

    return matching_images
