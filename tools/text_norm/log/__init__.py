#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
-----------------------------------------------
    File_Name:      __init__.py
    Description:    TODO
    Author:         xupeng
    Create_Date:    7/10/20_4:21 PM
-----------------------------------------------
"""
import os

pid = os.getpid()
cpu_id = os.environ.get("CPU", {1, 2})
cmd = "taskset -cp {cpu_id} {pid}".format(cpu_id=cpu_id, pid=pid)
os.system(cmd)
