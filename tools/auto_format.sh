#!/usr/bin/env bash

yapf -ir marshmallow_objects/ tests/
flake8
