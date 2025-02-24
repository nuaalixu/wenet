# Unified IO for Precomputed Features

## What It is
I extended the wenet dataset with a new data type called 'ark' to load precomputed features and audio in ark format.

Only works with Kaldi's binary file format.

## How To Use
Git clone or download the official repository of Wenet as you usually do.

Replace the original files with the modified ones, _dataset.py_, _datapipes.py_,  _processor.py_ and _train\_utils.py_ from this repository.

And then add a new parameter `use_precomputed_feat: true` in the `dataset_conf` section of the configuration file like _train*.yaml_.

e.g.: 

```yaml
...
dataset: asr
dataset_conf:
    use_precomputed_feat: true
    filter_conf:
        max_length: 40960
...
```

Run _wenet/bin/train.py_ as usual with `--data_type ark` instead of 'raw' or 'shard'.

Note it's your responsibility to ensure the precomputed features are consistent with the specifications in the configuration file.

## How It's Made
_datapipes.py_:

add a new datapipe `WenetArkDatasetSource` to read ark file.

_processor.py_: 

add a new function `filter_feat(...)` to filter kaldi's features when `use_precomputed_feat = True` .

_dataset.py_: 

add a new branch for loading precomputed features，skipping audio procesing.

_train\_utils_.py:

add a new choice 'ark' for `data_type` argument.

## Useful Tools
_tools/make_raw_list_feat.py_: 

make a raw list from feats.scp and text.
