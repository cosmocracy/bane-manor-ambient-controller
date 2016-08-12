FROM jfloff/alpine-python:2.7-onbuild
ADD run.py
ADD requirements.txt
CMD python run.py