python -m pip install --upgrade pip
echo "" > dna/secret
pip install -r requirements.txt
python setup.py build_ext --inplace