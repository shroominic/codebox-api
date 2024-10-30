ruff lint . --fix

# check if uv is installed or install it
if ! command -v uv &> /dev/null
then
    echo "uv not found, installing..."
    pip install uv
else
    echo "uv is already installed"
fi

# check if venv exists or create it
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv
else
    echo "Virtual environment already exists"
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install -r pyproject.toml

