#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest


def test_import_real_github_repo():
    from packyou.github.llazzaro.test_scripts.test import function1

    assert function1() == 'it works!'
