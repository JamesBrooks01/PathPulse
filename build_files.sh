# build_files.sh
pip install requirements.txt

# make migrations
python3 manage.py migrate 
python3 manage.py collectstatic