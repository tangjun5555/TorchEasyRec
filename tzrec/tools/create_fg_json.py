# Copyright (c) 2024, Alibaba Group;
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import json
import os

from tzrec.features.feature import create_fg_json
from tzrec.main import _create_features, _get_dataloader
from tzrec.utils import config_util

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pipeline_config_path",
        type=str,
        default=None,
        help="Path to pipeline config file.",
    )
    parser.add_argument(
        "--fg_output_dir",
        type=str,
        default=None,
        help="Directory to output feature generator json file.",
    )
    parser.add_argument(
        "--reserves",
        type=str,
        default=None,
        help="Reserved column names, e.g. label,request_id.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="debug feature config and fg json or not.",
    )
    args, extra_args = parser.parse_known_args()

    pipeline_config = config_util.load_pipeline_config(args.pipeline_config_path)
    features = _create_features(
        list(pipeline_config.feature_configs), pipeline_config.data_config
    )

    if args.debug:
        pipeline_config.data_config.num_workers = 1
        dataloader = _get_dataloader(
            pipeline_config.data_config, features, pipeline_config.train_input_path
        )
        iterator = iter(dataloader)
        _ = next(iterator)

    if not os.path.exists(args.fg_output_dir):
        os.makedirs(args.fg_output_dir)

    fg_json = create_fg_json(features, asset_dir=args.fg_output_dir)
    if args.reserves is not None:
        reserves = []
        for column in args.reserves.strip().split(","):
            reserves.append(column.strip())
        fg_json["reserves"] = reserves

    with open(os.path.join(args.fg_output_dir, "fg.json"), "w") as f:
        json.dump(fg_json, f, indent=4)