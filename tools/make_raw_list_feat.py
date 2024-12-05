#!/usr/bin/env python3

# Copyright (c) 2021 Mobvoi Inc. (authors: Binbin Zhang)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='use precomputed feat instead of wav')
    parser.add_argument('feat_file', help='feat file from kaldi')
    parser.add_argument('text_file', help='text file')
    parser.add_argument('output_file', help='output list file')
    args = parser.parse_args()

    feat_table = {}
    with open(args.feat_file, 'r', encoding='utf8') as fin:
        for line in fin:
            arr = line.strip().split()
            assert len(arr) == 2
            feat_table[arr[0]] = arr[1]

    with open(args.text_file, 'r', encoding='utf8') as fin, \
         open(args.output_file, 'w', encoding='utf8') as fout:
        for line in fin:
            arr = line.strip().split(maxsplit=1)
            key = arr[0]
            txt = arr[1] if len(arr) > 1 else ''

            assert key in feat_table
            feat = feat_table[key]
            line = dict(key=key, feat=feat, txt=txt)

            json_line = json.dumps(line, ensure_ascii=False)
            fout.write(json_line + '\n')
