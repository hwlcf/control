#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    run.py
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    App start point. Run python server to start app
    
"""
from gevent import monkey
# Monkey patch to support coroutine
# Must be at the start of the whole app
monkey.patch_all()

try:
    from gevent.wsgi import WSGIServer
except Exception:
    from gevent.pywsgi import WSGIServer

from app import app
from configs import AppConf


if app.debug:
    # Run with reloader
    from werkzeug.serving import run_with_reloader

    http_server = WSGIServer(('0.0.0.0', AppConf.PORT), app)

    @run_with_reloader
    def run_server():
        http_server.serve_forever()
else:

    http_server = WSGIServer((AppConf.BIND_IP, AppConf.PORT), app)
    http_server.serve_forever()
