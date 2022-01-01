# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01a_datasets.ipynb (unless otherwise specified).

__all__ = ['show_img', 'save_img', 'save_img_annotations', 'draw_grid', 'draw_bbox', 'bb_intersection_over_union',
           'sample_bbox', 'draw_rectangle', 'draw_ellipse', 'create_color_classification',
           'create_shape_color_classification', 'create_object_detection']

# Internal Cell
import numpy as np
import pandas as pd
from pandas import DataFrame
import ipywidgets as widgets
from pathlib import Path
import json
from skimage.draw import random_shapes
from random import randint
import matplotlib.pyplot as plt

# Internal Cell
from PIL import Image, ImageDraw
from skimage.draw import (rectangle, rectangle_perimeter, line)
from skimage.io import imsave

# Cell
def show_img(img):
    """
    Display a numpy array as a image
    """
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(3, 3))
    ax.imshow(img)

# Cell
def save_img(path, name, img):
    """
    Save a numpy array as a image
    """
    image = img.astype(np.uint8)
    filename = path/(name + ".jpg")

    imsave(filename, image, check_contrast=False)

# Cell
def save_img_annotations(path, annotations, name="annotations"):
    """
    Helper to save the annotations of a image into the desired file
    """
    filename = path/(name + ".json")

    with open(filename, "w") as file:
        json.dump(annotations, file)

# Cell
def draw_grid(im=None, size=(100, 100), n_hlines=10, n_vlines=10, black=True):
    """
    Will draw the default background with a grid system.

    im  np.array:
        Existing image, if None will create one

    size  (int, int):
        Height and width, respectively

    n_hlines  int:
        Number of horizontal lines

    n_vlines  int:
        Number of vertial lines

    black  bool:
        If true, the background will be black

    """
    height, width = size
    img = im
    color = (0, 0, 0)
    line_color = (1, 1, 1)
    if not black:
        color = (1, 1, 1)
        line_color = (0, 0, 0)

    if im is None:
        img = np.full((height, width, 3), dtype=np.double, fill_value=color)

    for l in range(n_hlines):
        y = height * l * (1 / n_hlines)
        y = int(y)
        rr_line, cc_line = line(0, y, width-1, y)
        img[rr_line, cc_line, :] = line_color

    for l in range(n_vlines):
        x =  width * l * (1 / n_vlines)
        x = int(x)
        rr_line, cc_line = line(x, 0, x, height-1)
        img[rr_line, cc_line, :] = line_color

    return img

# Cell

def draw_bbox(rect, rect_dimensions, im=None, black=True):
    """
    Draw a Bounding Box

    rect  (int, int):
        Begining point of the retangle

    rect_dimensions  (int, int):
        Width and Height of the retangle

    im  np.array:
        Image where bbox will be draw

    black  bool:
        If true, the bbox will be black

    """
    init_x, init_y = rect
    height, width = rect_dimensions
    img = im

    if im is None:
        img = np.ones((100, 200, 3), dtype=np.double)

    color = (0,0,0)
    if not black:
        color = (255, 255, 255)

    rr, cc = rectangle_perimeter(start=(init_x, init_y),
                                 extent=(height, width),
                                 shape=img.shape)
    img[rr, cc, :] = color

    ex_height = height + 10
    ex_width = width + 10
    if (ex_height > len(img)):
        ex_height = len(img)

    if (ex_width > len(im[0])):
        ex_width = len(img[0])

    rr, cc = rectangle_perimeter(start=(init_x-5, init_y-5),
                                 extent=(ex_height, ex_width),
                                 shape=img.shape)

    img[rr, cc, :] = color

    return img

# Internal Cell

def xywh_to_xyxy(boxes):
    boxes = np.array(boxes)
    """Convert [x y w h] box format to [x1 y1 x2 y2] format."""
    return np.hstack((boxes[0:2], boxes[0:2] + boxes[2:4])).tolist()

def xyxy_to_xywh(boxes):
    boxes = np.array(boxes)
    """Convert [x1 y1 x2 y2] box format to [x y w h] format."""
    return np.hstack((boxes[0:2], boxes[2:4] - boxes[0:2])).tolist()


# Internal Cell
def bbox_intersection(b1_coords, b1_dimensions, b2_coords, b2_dimensions):
    """
    determine the (x, y)-coordinates of the intersection rectangle

    b1_coords  (int, int):
        The origin of the bbox one

    b2_coords  (int, int):
        THe origin of the bbox two

    b1_dimensions  (int, int):
        The width and heigh of bbox one

    b2_dimensions  (int, int):
        The width and heigh of bbox two
    """
    xA = max(b1_coords[0], b2_coords[0])
    yA = max(b1_coords[1], b2_coords[1])

    b1_final_x = b1_dimensions[0] + b1_coords[0]
    b1_final_y = b1_dimensions[1] + b1_coords[1]
    b2_final_x = b2_dimensions[0] + b2_coords[0]
    b2_final_y = b2_dimensions[1] + b2_coords[1]

    xB = min(b1_final_x, b2_final_x) - xA
    yB = min(b1_final_y, b2_final_y) - yA

    # compute the area of intersection rectangle
    interArea = max(0, xB) * max(0, yB)

    # compute the area of both the prediction and ground-truth
    # rectangles
    b1Area = b1_dimensions[0] * b1_dimensions[1]
    b2Area = b2_dimensions[0] * b2_dimensions[1]

    return interArea, b1Area, b2Area, (xA, yA, xB, yB)

# Internal Cell
def overlap(boxA, boxA_dimensions, boxB, boxB_dimensions):
    """
    Returns the max relative overlap between two bboxs.
    """
    interArea, boxAArea, boxBArea, _ = bbox_intersection(boxA, boxA_dimensions,
                                                         boxB, boxB_dimensions)

    return max(interArea / float(boxAArea), interArea / float(boxBArea))

# Cell
def bb_intersection_over_union(boxA, boxA_dimensions, boxB, boxB_dimensions, verbose=False):
    interArea, boxAArea, boxBArea, _ = bbox_intersection(boxA, boxA_dimensions,
                                                         boxB, boxB_dimensions)

    iou = interArea / float(boxAArea + boxBArea - interArea)
    if verbose:
        print(f"iou: {iou: .2f}, interArea: {interArea: .2f}, boxAArea {boxAArea: .2f}, box1Area {boxBArea: .2f}")
    return iou

# Cell
def sample_bbox(bboxs=(), canvas_size=(100, 100), diag=(0.3, 0.3), ratio=(1, 1),
                max_iou=0.0, max_overlap=0.0,
                max_tries=1000, random_seed=None):
    """
    bboxs  [(x, y, x, y), ... ]:
        List of existing bboxs

    canvas_size  (int, int):
        Width and height on which to position the new bbox.

    max_iou  float [0, 1]:
        Maximum acceptable intersection over union between any two bboxs

    max_overlap  float [0, 1]:
        Maximum overlap between any two bboxs

    diag  (float, float) or float:
        Range of acceptable diagonal lenght relative to canvas diagonal

    ratio  (float, float) or float:
        Range of acceptable width / heigh ratios of the new bbox

    max_tries  int:
        Number of random tries to create a valid bbox
    """
#     for v in [diag, ratio]: assert min(v) >= 0 and max(v) <= 1, f"{v} is outside of (0, 1)"

    rng = np.random.RandomState(random_seed)
    width, height = canvas_size
    canvas_diag = np.sqrt(width ** 2 + height**2)

    for i in range(max_tries):
        s_diag = np.random.uniform(*diag) * canvas_diag
        s_ratio = np.random.uniform(*ratio)

        # sample position fully inside canvas
        s_height = np.sqrt(s_diag ** 2 / (1. + s_ratio ** 2))
        s_width = s_ratio * s_height

        cx = np.random.randint(s_width / 2, width - s_width / 2)
        cy = np.random.randint(s_height / 2, height - s_height / 2)

        bbox_x = cx - s_width / 2
        bbox_y = cy - s_height / 2
        bbox_width = cx + s_width / 2 - bbox_x
        bbox_height = cy + s_height / 2 - bbox_y

        bbox = (bbox_x, bbox_y, bbox_width, bbox_height)
        bbox = tuple(int(v) for v in bbox)

        # check if valid iou then return
        if len(bboxs) == 0:
            return bbox
        violation = False
        for b in bboxs:
            b_x, b_y, b_width, b_heigh = b
            iou = bb_intersection_over_union((b_x, b_y), (b_width, b_heigh),
                                             (bbox_x, bbox_y), (bbox_width, bbox_height))
            b_overlap = overlap((b_x, b_y), (b_width, b_heigh),
                                (bbox_x, bbox_y), (bbox_width, bbox_height))
            if iou > max_iou or b_overlap > max_overlap:
                violation = True
        if not violation:
            return bbox

    return None

# Cell
def draw_rectangle(im, start, dimensions, color):
    #draw = ImageDraw.Draw(im)
    #draw.rectangle(bbox, fill=color)
    rr, cc = rectangle(start=start, extent=dimensions)
    im[rr, cc, :] = color
    return im

# Cell
def draw_ellipse(im, start, dimensions, color):
    #draw = ImageDraw.Draw(im)
    #cx, cy = bbox[0] + bbox[2] / 2, bbox[1] + bbox[3]
    #draw.ellipse(bbox, fill=color)
    x, y = start
    v_radius, h_radius = dimensions

    rr, cc = ellipse(x, y, v_radius, h_radius)
    im[rr, cc, :] = color
    return im

# Internal Cell
def create_simple_object_detection_dataset(path, n_samples=100, n_objects_max=3, n_objects_min=1,
                                           size=(150, 150), min_size=0.2):
    (path/'images').mkdir(parents=True, exist_ok=True)
    (path/'class_images').mkdir(parents=True, exist_ok=True)

    min_dimension = size[0]
    if (size[1] < size[0]):
        min_dimension = size[1]

    # create class labels
    cname = ['red', 'green', 'blue']
    color = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    for clr, name in zip (color, cname):
        img_name = f'{name}'
        img = np.ones((50, 50, 3), dtype=np.uint8)
        draw_rectangle(img, start=(0, 0), dimensions=(50, 50), color=clr)
        save_img(path/'class_images', img_name, img)

    type_shapes = ['rectangle', 'circle', 'ellipse']
    # create images + annotations
    annotations = {}
    images = {}
    for i in range(n_samples):
        labels = []
        bboxs = []
        img_name = f'img_{i}'

        image, shapes = random_shapes(size, n_objects_max, multichannel=True,
                                      shape=type_shapes[randint(0, 2)],
                                      min_shapes=n_objects_min,
                                      min_size=min_size*min_dimension)

        for shape in shapes:
            shape_name = shape[0]
            rr_0, rr_1 = shape[1][0]
            cc_0, cc_1 = shape[1][1]
            middle_x = int((rr_0 + rr_1) / 2)
            middle_y = int((cc_0 + cc_1) / 2)

            label = (image[middle_x, middle_y].tolist(), shape_name)
            bbox = (int(cc_0), int(rr_0), int(cc_1), int(rr_1))
            labels.append(label)
            bboxs.append(bbox)

        img_file = img_name + ".jpg"
        images[img_file] = image
        save_img(path/'images', img_name, image)
        annotations[img_file] = {'labels': labels, 'bboxs': bboxs}

    save_img_annotations(path, annotations)
    return (images, annotations)

# Cell
def create_color_classification(path, n_samples=10, size=(150, 150)):
    """
    Helper function to color classification
    """

    images, annotations = create_simple_object_detection_dataset(path=path, n_samples=n_samples,
                                                                 size=size)

    color_img = {}
    for img in annotations:
        color_arr = []

        for shape in annotations[img]['labels']:
            color_arr.append(shape[0])

        color_img[img] = {'label': color_arr }

    save_img_annotations(path, color_img)
    return (images, color_img)

# Cell
def create_shape_color_classification(path, n_samples=10, size=(150, 150)):
    """
    Helper function to shape classification
    """
    images, annotations = create_simple_object_detection_dataset(path, n_samples=n_samples, size=size)

    label_img = {}
    for img in annotations:
        label_arr = []

        for shape in annotations[img]['labels']:
            label_arr.append(shape)

        label_img[img] = {'label': label_arr }

    save_img_annotations(path, label_img)
    return (images, label_img)

# Cell
def create_object_detection(path, n_samples=10, n_objects=1, size=(150, 150), multilabel=False):
    """
    Helper function to object detection
    """
    images, annotations = create_simple_object_detection_dataset(path=path,size=size,
                                                                 n_samples=n_samples,
                                                                 n_objects_max=n_objects)

    coords_img = {}
    for img in annotations:
        coords_arr = []

        for coord in annotations[img]['bboxs']:
            coords_arr.append(coord)

        if not multilabel:
            coords_arr = coords_arr[0]

        coords_img[img] = {'label': coords_arr }

    save_img_annotations(path, coords_img)
    return (images, coords_img)