echo "[INFO]: start pre-commit script"
echo "[INFO]: flake8 stage"

python -m flake8 src/test_system

if [ $? -ne 0 ]; then
    echo "[ERROR]: flake8 stage failed"
    exit 1
fi

echo "[INFO]: pre-commit successfully completed"
