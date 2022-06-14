ARG BASE_CONTAINER=condaforge/mambaforge:latest
FROM $BASE_CONTAINER

SHELL ["/bin/bash", "-c"]

ARG python=3.8

ENV PATH /opt/conda/bin:$PATH
ENV PYTHON_VERSION=${python}

RUN mamba install -y \
    python=${PYTHON_VERSION} \
    bokeh \
    nomkl \
    cmake \
    python-blosc \
    cytoolz \
    dask \
    lz4 \
    numpy \
    pandas \
    tini==0.18.0 \
    cachey \
    streamz \
    && mamba clean -tipy \
    && find /opt/conda/ -type f,l -name '*.a' -delete \
    && find /opt/conda/ -type f,l -name '*.pyc' -delete \
    && find /opt/conda/ -type f,l -name '*.js.map' -delete \
    && find /opt/conda/lib/python*/site-packages/bokeh/server/static -type f,l -name '*.js' -not -name '*.min.js' -delete \
    && rm -rf /opt/conda/pkgs

# Install requirements.txt defined libraries
COPY requirements.txt /tmp/
RUN python -m pip install --upgrade pip \
    && pip install --requirement /tmp/requirements.txt

#RUN apt-get install libsqlite3-dev
#RUN ./configure --enable-loadable-sqlite-extensions && make && sudo make install

# Create the environment:
COPY environment.yml /tmp/
RUN conda env create -f /tmp/environment.yml

# Activate the environment, and make sure it's activated:
RUN source activate nc2zarr

# Install nc2zarr
COPY nc2zarr/ ./nc2zarr/
COPY setup.py .
RUN python setup.py develop

# Copy notebooks and nc2zarr templates
COPY notebooks/ ./notebooks/
COPY nc2zarr-configs/ ./nc2zarr-templates/
COPY custom-processors/ ./custom-processors/

RUN export PYTHONPATH=${PYTHONPATH}:./custom-processors

RUN mkdir /opt/app