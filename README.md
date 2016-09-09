# packyou
[![Build Status](https://travis-ci.org/llazzaro/packyou.svg?branch=master)](https://travis-ci.org/llazzaro/packyou) [![Code Health](https://landscape.io/github/llazzaro/packyou/master/landscape.svg?style=flat)](https://landscape.io/github/llazzaro/packyou/master) [![Coverage Status](https://coveralls.io/repos/github/llazzaro/packyou/badge.svg)](https://coveralls.io/github/llazzaro/packyou)

## Description
Downloads a python project from github and allows to import it from anywhere. Very useful when the repo is not a package

## Introduction

Sometimes is usefull to be able to import a project from github.
If the project is configured as a python package it could be installed with pip and git.
But still lot of project are not using setuptools which makes difficult to use them from python easily.
Some people could be using git submodules, but it also requires adding a __init__.py file in the project root.

With packyou it is possible to import any pure python project from github justo with a simple import statement like:

"from packyou.github.username.report import external_github_repo"

* Free software: MIT license
* Documentation: https://packyou.readthedocs.io.


## Features
--------

* Add support for bitbucket, gitlab
