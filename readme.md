# gitmirror
This is a web service to handle bitbucket commit hook POST requests.

Similar to https://github.com/dustin/gitmirror, but wrtten using python.

# install
You need python2 > 2.7.9 for the ssl stuff otherwise any other python2 will work

## virtualenv
    sudo apt-get install python-virtualenv
    virtualenv --python=/full/path/to/python2.binary env
    source env/bin/activate
    pip install -r requirements

# test
    # start the service on localhost:8080
    # and create a mirror of https://github.com/afrantisak/git-mirror-webhook.git 
    # in ./test/testrepo
    ./service.py 

