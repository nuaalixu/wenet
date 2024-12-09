# Unified IO for precomputed feature

## What It is
I modified the wenet dataset to load precomputed features from kaldi, supporting both raw and shard modes.

Only works with Kaldi's binary file format

## How To Use
You only need to replace the original files with the modified ones, _dataset.py_ and _processor.py_.

And then add a new parameter `use_precomputed_feat: true` in the `dataset_conf` section of the configuration file _config.yaml_.

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

Note you need to manually ensure that the precomputed features are consistent with the specifications in the configuration file.

## How It's Made
_processor.py_: 

add a new function `decode_feat(sample)` to load kaldi's features with `kaldi_io`.

use a fake wav field for compatibility.

_dataset.py_: 

add a new branch for loading precomputed features，skipping audio procesing.

## Useful Tools
_tools/make_raw_list_feat.py_: 

make raw list from feats.scp and text.

_tools/make_shard_list_feat.py_: 

make shard list from feats.scp and text without audios included.

