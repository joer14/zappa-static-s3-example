example project for zappa s3 static pr.

how to edit zappa:

- mkvirtualenv zappa
- pip install zappa
- then edit these files:
     atom ~/.virtualenvs/zappa/lib/python2.7/site-packages/zappa/
- once everything is good, copy the edited files into a new forked zappa repo and try to create a pr or whatever.



stuff in here:

example zappa_settings files
example app.py
bootstrap_aws.py - some code that partially does what I want.
example build dir with index.html and an image for testing loading external resources.
