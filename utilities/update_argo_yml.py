# !/usr/bin/python
import yaml
import re
import subprocess
import fsspec
import os
import time

start_time = time.time()
config_file = "./configs/argo/argo_1.yml"
fs = fsspec.filesystem('s3', anon=True)
all_files = fs.glob(f's3://imos-data-pixeldrill/viet-test/argo/converted/*.nc')
os.environ["AWS_PROFILE"] = "nonproduction-admin"

print('*********************************************\n')

for file in all_files:
    filename = re.search('[\w-]+?(?=\.)', file)[0]

    with open(config_file) as istream:
        ymldoc = yaml.safe_load(istream)
        print('Processing file: ', filename)
        ymldoc['input']['paths'] = re.sub('[\w-]+?(?=\.)', filename, ymldoc['input']['paths'])
        # regex that replacing last folder from path
        ymldoc['output']['path'] = re.sub('([^\/]+)(?=.$)', filename, ymldoc['output']['path'])

    with open(config_file, "w") as ostream:
        yaml.dump(ymldoc, ostream, default_flow_style=False, sort_keys=False)

    subprocess.run(["nc2zarr", "-c", "./configs/argo/argo_1.yml"])

print('\n*********************************************')
print("---------- Total: %.2f seconds ----------" % (time.time() - start_time))
print('*********************************************')