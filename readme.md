# git-mirror-webhook
This is a web service that pulls a git repository in response to bitbucket commit hook POST requests.  
TODO: handle github hooks also.

Similar to https://github.com/dustin/gitmirror, but in python.

# install
## virtualenv
    apt-get install python-virtualenv
    virtualenv --python=/usr/bin/python2 env
    source env/bin/activate
    pip install -r requirements

# test
    # start the service on localhost:8080
    # and create a mirror of https://github.com/afrantisak/git-mirror-webhook.git 
    # in ./test/testrepo
    ./service.py 

# ssl
If you want an ssl server, you will need python 2.7.9 or better.  To build a specific version:

    wget http://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz
    tar xf Python-2.7.9.tgz 
    mkdir ~/python2.7.9
    cd Python-2.7.9/
    ./configure --prefix=/home/<user>/python2.7.9
    make install

Then you will need to change the `virtualenv env` line above to 

    virtualenv --python=/home/<user>/python2.7.9 env

