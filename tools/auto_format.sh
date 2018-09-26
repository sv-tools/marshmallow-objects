#!/usr/bin/env bash

yapf -ir marshmallow_objects/ tests/ tools/bump_version
flake8
