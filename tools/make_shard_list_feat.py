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
import io
import logging
import os
import tarfile
import time
import multiprocessing

import wenet.dataset.kaldi_io as kaldi_io


def write_tar_file(data_list,
                   tar_file,
                   index=0,
                   total=1):
    logging.info('Processing {} {}/{}'.format(tar_file, index, total))
    read_time = 0.0
    save_time = 0.0
    write_time = 0.0
    with tarfile.open(tar_file, "w") as tar:
        for item in data_list:
            key, txt, feat = item

            assert isinstance(feat, str)
            ts = time.time()
            feat = kaldi_io.read_mat(feat)
            read_time += (time.time() - ts)

            ts = time.time()

            file_obj= io.BytesIO()
            file_obj.mode = 'wb'  # for kaldi_io check
            kaldi_io.write_mat(file_obj, feat)
            suffix = "feat"
            file_obj.seek(0)
            data = file_obj.read()
            save_time += (time.time() - ts)

            assert isinstance(txt, str)
            ts = time.time()
            txt_file = key + '.txt'
            txt = txt.encode('utf8')
            txt_data = io.BytesIO(txt)
            txt_info = tarfile.TarInfo(txt_file)
            txt_info.size = len(txt)
            tar.addfile(txt_info, txt_data)

            feat_file = key + '.' + suffix
            feat_data = io.BytesIO(data)
            feat_info = tarfile.TarInfo(feat_file)
            feat_info.size = len(data)
            tar.addfile(feat_info, feat_data)
            write_time += (time.time() - ts)
        logging.info('read {} save {} write {}'.format(read_time, save_time,
                                                       write_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--num_utts_per_shard',
                        type=int,
                        default=1000,
                        help='num utts per shard')
    parser.add_argument('--num_threads',
                        type=int,
                        default=1,
                        help='num threads for make shards')
    parser.add_argument('--prefix',
                        default='shards',
                        help='prefix of shards tar file')

    parser.add_argument('feat_file', help='feat file from kaldi')
    parser.add_argument('text_file', help='text file')
    parser.add_argument('shards_dir', help='output shards dir')
    parser.add_argument('shards_list', help='output shards list file')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    feat_table = {}
    with open(args.feat_file, 'r', encoding='utf8') as fin:
        for line in fin:
            arr = line.strip().split()
            assert len(arr) == 2
            feat_table[arr[0]] = arr[1]

    data = []
    with open(args.text_file, 'r', encoding='utf8') as fin:
        for line in fin:
            arr = line.strip().split(maxsplit=1)
            key = arr[0]
            txt = arr[1] if len(arr) > 1 else ''

            assert key in feat_table
            feat = feat_table[key]
            data.append((key, txt, feat))

    num = args.num_utts_per_shard
    chunks = [data[i:i + num] for i in range(0, len(data), num)]
    os.makedirs(args.shards_dir, exist_ok=True)

    # Using thread pool to speedup
    pool = multiprocessing.Pool(processes=args.num_threads)
    shards_list = []
    tasks_list = []
    num_chunks = len(chunks)
    for i, chunk in enumerate(chunks):
        tar_file = os.path.join(args.shards_dir,
                                '{}_{:09d}.tar'.format(args.prefix, i))
        shards_list.append(tar_file)
        pool.apply_async(
            write_tar_file,
            (chunk, tar_file, i, num_chunks))

    pool.close()
    pool.join()

    with open(args.shards_list, 'w', encoding='utf8') as fout:
        for name in shards_list:
            fout.write(name + '\n')
