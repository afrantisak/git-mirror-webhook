# gitmirror
This is a web service to handle bitbucket commit hook POST requests.

Similar to https://github.com/dustin/gitmirror, but wrtten using python.

# install
You need python2 > 2.7.9 for the ssl stuff otherwise any other python2 will work

## virtualenv
    virtualenv --python=/full/path/to/python2.binary env
    source env/bin/activate
    pip install -r requirements

# test
    # this will start the service on localhost:8080 and create a mirror of git@github.com:afrantisak/gitmirror.git in test/testrepo
    ./service.py 

