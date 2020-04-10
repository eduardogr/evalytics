# Contributing to Evalytics

Thanks for checking out Evalytics!

## Table of Contents

0. [Types of contributions we're looking for](#types-of-contributions-were-looking-for)
0. [Ground rules & expectations](#ground-rules--expectations)
0. [How to contribute](#how-to-contribute)
0. [Setting up your environment](#setting-up-your-environment)

## Types of contributions we're looking for
There are many ways you can directly contribute to Evalytics:

* Finding/Fixing bugs.
* Adding new features.
* Extending/Improving documentation.
* Suggesting code style changes.

and feel free if you have other ways of contributing! 

Interested in making a contribution? Read on!

## Ground rules & expectations

Before we get started, here are a few things we expect from you (and that you should expect from others):

* Be kind and thoughtful in your conversations around this project. We all come from different backgrounds and projects, which means we likely have different perspectives on "how open source is done." Try to listen to others rather than convince them that your way is correct.
* Open Source Guides are released with a [Contributor Code of Conduct](./CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.
* If you open a pull request, please ensure that your contribution passes all tests. If there are test failures, you will need to address them before we can merge your contribution.
* When adding content, please consider if it is widely valuable. Please don't add references or links to things you or your employer have created as others will do so if they appreciate it.

## How to contribute

If you'd like to contribute, start by searching through the [issues](https://github.com/eduardogr/evalytics/issues) and [pull requests](https://github.com/eduardogr/evalytics/pulls) to see whether someone else has raised a similar idea or question.

If you don't see your idea listed, and you think it fits into the goals of this guide, do one of the following:
* **If your contribution is minor,** such as a typo fix, open a pull request.
* **If your contribution is major,** such as a new guide, start by opening an issue first. That way, other people can weigh in on the discussion before you do any work.

## Setting up your environment

This API is powered by Python + Tornado. 

Running it on your local machine requires the installation of
  - [Python3.6+](https://www.python.org/downloads/release/python-360/) 
  - [Python pip + virtual envs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

and you'll need to have your *PYTHONPATH* environment variable with the value of the path of this repository's root
  - e.g. /home/myuser/repos/evalytics

Optionally you can running it on your local machine with [docker](https://www.docker.com/) + [make](https://www.gnu.org/software/make/manual/html_node/Introduction.html), running:
  - make build
  - make google-auth
  - make run-server

Once you have that set up, run:

  - ping localhost:8080/

And check that the server it's up and runnning.
