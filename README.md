[![Build Status](https://github.com/vietnguyengit/nc2zarr/workflows/Build%20CI/badge.svg)](https://github.com/vietnguyengit/nc2zarr/actions)

# nc2zarr

A Python tool that converts multiple NetCDF files to single Zarr datasets.

### Using nc2zarr on AWS stacks

* Use stackman to deploy AWS stacks for this repo with Cloudformation.

* In SageMaker notebook instance, open a terminal tab, then activate `nc2zarr` env with `source activate nc2zarr`, then `cd` to working directory `cd SageMaker/nc2zarr`.

* To use custom processors with `nc2zarr`, issue command:

    `export PYTHONPATH=${PYTHONPATH}:/home/ec2-user/SageMaker/nc2zarr/custom-processors`
    
    Don't need to export `PYTHONPATH` if using `nc2zarr` from a Docker container.

* To use `nc2zarr`:

    `nc2zarr -c <path to config file>`

----------

## Below is original README.md from `nc2zarr` developers

### Create Python environment

    $ conda install -n base -c conda-forge mamba
    $ cd nc2zarr
    $ mamba env create

### Install nc2zarr from Sources

    $ cd nc2zarr
    $ conda activate nc2zarr
    $ python setup.py develop

### Testing and Test Coverage

    $ pytest --cov nc2zarr --cov-report=html tests   

### Usage

```
$ nc2zarr --help
Usage: nc2zarr [OPTIONS] [INPUT_FILE ...]

  Reads one or more input datasets and writes or appends them to a single
  Zarr output dataset.

  INPUT_FILE may refer to a NetCDF file, or Zarr dataset, or a glob that
  identifies multiple paths, e.g. "L3_SST/**/*.nc".

  OUTPUT_PATH must be directory which will contain the output Zarr dataset,
  e.g. "L3_SST.zarr".

  CONFIG_FILE must be in YAML format. It comprises the optional objects
  "input", "process", and "output". See nc2zarr/res/config-template.yml for
  a template file that describes the format. Multiple --config options may
  be passed as a chain to allow for reuse of credentials and other common
  parameters. Contained configuration objects are recursively merged, lists
  are appended, and other values overwrite each other from left to right.
  For example:

  nc2zarr -c s3.yml -c common.yml -c inputs-01.yml -o out-01.zarr
  nc2zarr -c s3.yml -c common.yml -c inputs-02.yml -o out-02.zarr
  nc2zarr out-01.zarr out-02.zarr -o final.zarr

  Command line arguments and options have precedence over other
  configurations and thus override settings in any CONFIG_FILE:

  [--finalize-only] overrides /finalize_only
  [--dry-run] overrides /dry_run
  [--verbose] overrides /verbosity

  [INPUT_FILE ...] overrides /input/paths in CONFIG_FILE
  [--multi-file] overrides /input/multi_file
  [--concat-dim] overrides /input/concat_dim
  [--decode-cf] overrides /input/decode_cf
  [--sort-by] overrides /input/sort_by

  [--output OUTPUT_FILE] overrides /output/path
  [--overwrite] overrides /output/overwrite
  [--append] overrides /output/append
  [--adjust-metadata] overrides /output/adjust_metadata

Options:
  -c, --config CONFIG_FILE   Configuration file (YAML). Multiple may be given.
  -o, --output OUTPUT_PATH   Output name. Defaults to "out.zarr".
  -d, --concat-dim DIM_NAME  Dimension for concatenation. Defaults to "time".
  -m, --multi-file           Open multiple input files as one block. Works for
                             NetCDF files only. Use --concat-dim to specify
                             the dimension for concatenation.

  -w, --overwrite            Overwrite existing OUTPUT_PATH. If OUTPUT_PATH
                             does not exist, the option has no effect. Cannot
                             be used with --append.

  -a, --append               Append inputs to existing OUTPUT_PATH. If
                             OUTPUT_PATH does not exist, the option has no
                             effect. Cannot be used with --overwrite.

  --decode-cf                Decode variables according to CF conventions.
                             Caution: array data may be converted to floating
                             point type if a "_FillValue" attribute is
                             present.

  -s, --sort-by [path|name]  Sort input files by specified property.
  --adjust-metadata          Adjust metadata attributes after the last
                             write/append step.

  --finalize-only            Whether to just run "finalize" tasks on an
                             existing output dataset. Currently, this updates
                             the metadata only, given that configuration
                             output/adjust_metadata is set or output/metadata
                             is not empty. See also option --adjust-metadata.

  -d, --dry-run              Open and process inputs only, omit data writing.
  -v, --verbose              Print more output. Use twice for even more
                             output.

  --version                  Show version number and exit.
  --help                     Show this message and exit.
```

### Configuration file format

The format of the configuration files passed via the `--config` option is described
as a [configuration template](https://github.com/bcdev/nc2zarr/blob/main/nc2zarr/res/config-template.yml).

### Examples

Convert multiple NetCDFs to single Zarr:

```bash
$ nc2zarr -o outputs/SST.zarr inputs/**/SST-*.nc
```

Append single NetCDF to an existing Zarr:

```bash
$ nc2zarr -a -o outputs/SST.zarr inputs/2020/SST-20200610.nc
```

Concatenate multiple Zarrs to a new Zarr:

```bash
$ nc2zarr -o outputs/SST.zarr outputs/SST-part1.zarr outputs/SST-part2.zarr
```

Append one Zarr to existing Zarr:

```bash
$ nc2zarr -a -o outputs/SST.zarr outputs/SST-part3.zarr
```

### Custom processors

nc2zarr's built-in processors can be expanded with _custom processors_, Python
functions which modify the dataset at particular points in the conversion
pipeline. A processor function takes an `xarray.Dataset` as an argument and
returns an `xarray.Dataset` as its result. A processor is specified in the
configuration file as `<MODULE_NAME>:<FUNCTION_NAME>`, so for example the
processor specification `mymodule:myfunction` could refer to a function
defined in a file `mymodule.py` with the following contents:

```python
def myfunction(dataset):
    dataset.attrs["greeting"] = "Hello world!"
    return dataset
```

This processor function adds a predefined attribute to the dataset (modifying
it in-place), then returns the modified dataset.

There are three points at which processors may be run:

| Section | Parameter name | When is the processor run? |
| -- | -- | -- |
| `input`   | `custom_preprocessor`  | After variable selection |
| `process` | `custom_processor` | After variable renaming, before rechunking |
| `output`  | `custom_postprocessor` | Before writing data |

See the template configuration file for more details of syntax. The module is
searched for on Python's current search path, so it will usually be necessary
to ensure that the parent directories of all processor modules are listed in
the `PYTHONPATH` environment variable, e.g. by executing

```shell
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}/path/to/module/directory/"
```

before running nc2zarr. See
[the Python documentation](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH)
for more details on `PYTHONPATH`.
