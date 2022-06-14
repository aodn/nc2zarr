# install pip libs
cd /home/ec2-user/SageMaker/nc2zarr
pip install -r requirements.txt

# install conda env
cd /home/ec2-user
conda activate base
yes | conda update -n base --force conda
yes | conda install -n base -c conda-forge mamba
cd /home/ec2-user/SageMaker/nc2zarr
mamba env create

source activate nc2zarr
python setup.py develop

# generate tests
pytest --cov nc2zarr --cov-report=html tests