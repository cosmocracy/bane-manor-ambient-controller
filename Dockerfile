FROM jfloff/alpine-python:2.7-onbuild
ADD run.py /tmp/
ADD requirements.txt /tmp/
CMD python /tmp/run.py
