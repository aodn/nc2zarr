#!/bin/bash

echo "******************************************************"

cd /home/ec2-user/SageMaker/nc2zarr/inputs/argo/1901126
#files=`ls *.nc`
for file in *.nc
do
  echo 'Processing file' "$file"
  nccopy -k 4 "$file" '/home/ec2-user/SageMaker/nc2zarr/inputs/argo/1901126/converted/'"$file"
done
