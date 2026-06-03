ENV_NAME ?= mcp-course
PYTHON_VERSION ?= 3.11
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

.PHONY: all conda-create env-setup pip-tools-setup repo-setup notebook-setup env-update clean test

all: conda-create env-setup repo-setup notebook-setup env-update

conda-create:
	conda create -n $(ENV_NAME) python=$(PYTHON_VERSION) -y

env-setup: conda-create
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	pip install --upgrade pip && \
	pip install uv && \
	uv pip install pip-tools setuptools ipykernel

repo-setup:
	mkdir -p requirements
	echo "ipykernel" > requirements/requirements.in

notebook-setup:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	python -m ipykernel install --user --name=$(ENV_NAME)

env-update:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	uv pip compile ./requirements/requirements.in -o ./requirements/requirements.txt && \
	uv pip sync ./requirements/requirements.txt

clean:
	conda env remove -n $(ENV_NAME)

freeze:
	$(CONDA_ACTIVATE) $(ENV_NAME) && \
	uv pip freeze > requirements/requirements.txt

# Run the offline test suite (no network, no LLM calls). Uses uv to
# pull deps on the fly so this works without any conda/venv setup.
test:
	MCP_AUTH_TOKEN=test-token uv run \
		--with pytest \
		--with mcp \
		--with ddgs \
		--with starlette \
		--with httpx \
		--with python-dotenv \
		--with claude-agent-sdk \
		pytest tests/ -q
