#!/bin/bash
exec gunicorn gestion_productos.wsgi --bind 0.0.0.0:${PORT:-8000} --workers 2 --log-file -
