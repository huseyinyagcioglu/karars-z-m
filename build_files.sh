#!/usr/bin/env bash
echo "Building Kararsızım project..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "Build complete!"
