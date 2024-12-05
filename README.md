# streamlit_study

## Installation

Clone this repository, create a new environment using `miniconda` or `micromamba` and install the dependencies

```bash
conda create -n streamlit
conda activate streamlit
conda install python=3.12 streamlit munch -c conda-forge
python -m pip install streamlit_survey pyrolific
```

## Preparations

1. Copy `sample_config.yml` to e.g. `config.yml` and change the values as required
1. Create an api token on prolific and save it to `api_token` or whatever you configured it to in `config.yml`
1. Create a new empty database for your study with `python init_db.py config.yml`

## Run

Run the study server using `streamlit run main.py config.yml`
