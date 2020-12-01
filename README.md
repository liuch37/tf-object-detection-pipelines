# tf-object-detection-pipelines
Customized train/inference pipelines of using TensorFlow object detection API [1] with TensorFlow 2.

## Installation
Follow the steps in [2].

## Command
Modify the model configurations, data loading, data preprocessing,...etc inside each code.

Train:
```
python train.py
```

Inference:
```
python inference.py
```

## Command line interface option
Check examples in [3] pasted below.

Train:
```
# From the tensorflow/models/research/ directory
PIPELINE_CONFIG_PATH={path to pipeline config file}
MODEL_DIR={path to model directory}
python object_detection/model_main_tf2.py \
    --pipeline_config_path=${PIPELINE_CONFIG_PATH} \
    --model_dir=${MODEL_DIR} \
    --alsologtostderr
```
where ${PIPELINE_CONFIG_PATH} points to the pipeline config and ${MODEL_DIR} points to the directory in which training checkpoints and events will be written.

Evaluation:
```
# From the tensorflow/models/research/ directory
PIPELINE_CONFIG_PATH={path to pipeline config file}
MODEL_DIR={path to model directory}
CHECKPOINT_DIR=${MODEL_DIR}
MODEL_DIR={path to model directory}
python object_detection/model_main_tf2.py \
    --pipeline_config_path=${PIPELINE_CONFIG_PATH} \
    --model_dir=${MODEL_DIR} \
    --checkpoint_dir=${CHECKPOINT_DIR} \
    --alsologtostderr
```
where ${CHECKPOINT_DIR} points to the directory with checkpoints produced by the training job. Evaluation events are written to ${MODEL_DIR/eval}.

## Reference
[1] https://github.com/tensorflow/models/tree/master/research/object_detection

[2] https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/install.html

[3] https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2_training_and_evaluation.md
