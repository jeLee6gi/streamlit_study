# streamlit_study

## Installation

Clone this repository, create a new environment using `miniconda` or `micromamba` and install the dependencies

```bash
conda create -n streamlit
conda activate streamlit
conda install python=3.12 streamlit munch pyyaml -c conda-forge
python -m pip install streamlit_survey pyrolific
```

## Preparations

1. Copy `sample_config.yml` to e.g. `config.yml` and change the values as required
1. Create an api token on prolific and save it to `api_token` or whatever you configured it to in `config.yml`
1. Create a new empty database for your study with `python init_db.py config.yml`

## Run

Run the study server using `streamlit run main.py config.yml`

### Running on uberspace

1. Open a TCP port using `uberspace port add` and remember the port number it gives you. You can retrieve it later though using the command `uberspace port list`. **NB it might take a few minutes for the updated firewall rules to take effect and the port actually being available from the outside.**

2. Run the server specifying the port you opened and the Let's Encrypt-certificates that uberspace provided you with so the encryption to your server is encrypted. Replace `${PORT}` with the port number uberspace opened for you and `${ASTEROID}` with the name you picked for you uberspace:

```
streamlit run --server.port ${PORT} --server.sslCertFile ~/etc/certificates/${ASTEROID}.uber.space.crt --server.sslKeyFile ~/etc/certificates/${ASTEROID}.uber.space.key main.py config.yml
```
