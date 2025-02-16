'''
This code is to use TensorFlow hub to retrive already trained object detection model for inference.
'''

#@title Imports and function definitions

# For running inference on the TF-Hub module.
import tensorflow as tf

import tensorflow_hub as hub

# For downloading the image.
import matplotlib.pyplot as plt
import tempfile
from six.moves.urllib.request import urlopen
from six import BytesIO

# For drawing onto the image.
import numpy as np
from PIL import Image
from PIL import ImageColor
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

# For measuring the inference time.
import time


def display_image(image):
    fig = plt.figure(figsize=(20, 15))
    plt.grid(False)
    plt.imsave('test.jpg', image)
    plt.imshow(image)
    plt.show()


def draw_bounding_box_on_image(image,
                               ymin,
                               xmin,
                               ymax,
                               xmax,
                               color,
                               font,
                               thickness=4,
                               display_str_list=()):
    """Adds a bounding box to an image."""
    draw = ImageDraw.Draw(image)
    im_width, im_height = image.size
    (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                  ymin * im_height, ymax * im_height)
    draw.line([(left, top), (left, bottom), (right, bottom), (right, top),
               (left, top)],
              width=thickness,
              fill=color)

    # If the total height of the display strings added to the top of the bounding
    # box exceeds the top of the image, stack the strings below the bounding box
    # instead of above.
    display_str_heights = [font.getsize(ds)[1] for ds in display_str_list]
    # Each display_str has a top and bottom margin of 0.05x.
    total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

    if top > total_display_str_height:
        text_bottom = top
    else:
        text_bottom = top + total_display_str_height
    # Reverse list and print from bottom to top.
    for display_str in display_str_list[::-1]:
        text_width, text_height = font.getsize(display_str)
        margin = np.ceil(0.05 * text_height)
        draw.rectangle([(left, text_bottom - text_height - 2 * margin),
                        (left + text_width, text_bottom)],
                       fill=color)
        draw.text((left + margin, text_bottom - text_height - margin),
                  display_str,
                  fill="black",
                  font=font)
        text_bottom -= text_height - 2 * margin


def draw_boxes(image, boxes, class_names, scores, max_boxes=10, min_score=0.1):
    """Overlay labeled boxes on an image with formatted scores and label names."""
    colors = list(ImageColor.colormap.values())

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Regular.ttf",
                                  25)
    except IOError:
        print("Font not found, using default font.")
        font = ImageFont.load_default()

    for i in range(min(boxes.shape[0], max_boxes)):
        if scores[i] >= min_score:
            ymin, xmin, ymax, xmax = tuple(boxes[i])
            #display_str = "{}: {}%".format(class_names[i].decode("ascii"),
            #                               int(100 * scores[i]))
            display_str = "{}: {}%".format(class_names[i], int(100 * scores[i]))
            color = colors[hash(class_names[i]) % len(colors)]
            image_pil = Image.fromarray(np.uint8(image)).convert("RGB")
            draw_bounding_box_on_image(
                image_pil,
                ymin,
                xmin,
                ymax,
                xmax,
                color,
                font,
                display_str_list=[display_str])
            np.copyto(image, np.array(image_pil))

    return image


def load_img(path):
    img = tf.io.read_file(path)
    img = tf.image.decode_jpeg(img, channels=3)
    return img


def coco_label_conversion(detection_classes, label_path):
    class_names = []
    file = open(label_path, "r")
    classes = file.read().splitlines()
    for cls_idx in detection_classes[0, :]:
        class_names.append(classes[int(cls_idx) - 1])

    return class_names


def run_detector(detector, image_path, label_path):
    img = load_img(image_path)

    #converted_img  = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
    converted_img  = tf.image.convert_image_dtype(img, tf.uint8)[tf.newaxis, ...]
    start_time = time.time()
    result = detector(converted_img)
    end_time = time.time()

    result = {key:value.numpy() for key,value in result.items()}

    print("Found %d objects." % len(result["detection_scores"][0, :]))
    print("Inference time: ", end_time-start_time)
    
    # For Faster RCNN
    #image_with_boxes = draw_boxes(
    #    img.numpy(), result["detection_boxes"],
    #    result["detection_class_entities"], result["detection_scores"])

    # For EfficientDet
    detection_class_entities = coco_label_conversion(result["detection_classes"], label_path)
    image_with_boxes = draw_boxes(
        img.numpy(), result["detection_boxes"][0, :],
        detection_class_entities, result["detection_scores"][0, :])


    display_image(image_with_boxes)


def run_feature_extraction(feature_extractor, height, width, image_path):
    img = load_img(image_path)

    converted_img  = tf.image.convert_image_dtype(img, tf.float32)[tf.newaxis, ...]
    converted_img = tf.image.resize(converted_img, [height, width])
    start_time = time.time()
    features = feature_extractor(converted_img)   # A batch with shape [batch_size, num_features].
    end_time = time.time()

    print("Inference time: ", end_time-start_time)

    return features


if __name__ == "__main__":
    # Configurations
    image_path = "./test_image/Naxos_Taverna.jpg"
    detection_module_handle = "./model/efficientdet_d6_1"
    #feature_module_handle = "./model/efficientnet_b6_feature-vector_1"
    feature_module_handle = "./model/resnet_50_feature_vector_1"
    label_path = "./util/coco-labels-paper.txt"

    # Print Tensorflow version
    print(tf.__version__)

    # Check available GPU devices.
    print("The following GPU devices are available: %s" % tf.test.gpu_device_name())

    # load model
    #detector = hub.load(detection_module_handle).signatures['default'] # for Faster RCNN
    detector = hub.load(detection_module_handle) # for EfficientDet

    # feature vector extractor
    feature_extractor = hub.load(feature_module_handle)
    #height, width = 528, 528 # EfficientNet
    height, width = 224, 224 # ResNet-50
    features = run_feature_extraction(feature_extractor, height, width, image_path)
    print(features.shape)

    # run inference
    run_detector(detector, image_path, label_path)
