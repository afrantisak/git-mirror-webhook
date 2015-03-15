#!/usr/bin/env python
import os
import git
import ssl
import time
import json
import flask
import flask.ext
import flask.ext.cors

def log(text):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print("{timestamp}: {message}".format(timestamp = timestamp, message = text))

def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

class Application():
    def __init__(self, config):
        self.config = config
        self.repo = self.create_or_use()
        self.pull()

    def create_or_use(self):
        repo_path = config['repo_path']
        if not os.path.exists(repo_path):
            _mkdir(repo_path)
            repo = git.Repo.init(repo_path)
        else:
            repo = git.Repo(repo_path)
        try:
            repo.remotes.origin
        except:
            remote = config['repo_remote']
            name = remote['name']
            url = remote['url']
            log("creating remote {name} => {url}".format(**locals()))
            repo.create_remote(name, url)
        return repo

    def pull(self):
        origin = self.repo.remotes.origin
        log('pulling')
        origin.pull(**{'ff-only': True})
        log('checkout')
        master = self.repo.create_head('master', origin.refs.master)
        master.set_tracking_branch(origin.refs.master)
        master.checkout()
        
def git_hook_service(config):
    rest_service = flask.Flask(config['app_name'])

    # load ssl certificate for https
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(config['ssl_cert_filepath'], config['ssl_key_filepath'])

    # set up cross-origin resource sharing (CORS)
    cors = flask.ext.cors.CORS(rest_service, allow_headers='X-Requested-With')
    rest_service.config['CORS_HEADERS'] = 'X-Requested-With'

    application = Application(config)
    
    # commit hook handler
    @rest_service.route("/bitbucket_commit_hook", methods=['POST'])
    @flask.ext.cors.cross_origin()
    def commit_hook():
        data = json.loads(flask.request.data)
        auth = flask.request.authorization
        if auth['username'] != config['auth_username'] or auth['password'] != config['auth_password']:
            log("Invalid username/password: {username}/{password}".format(username=auth['username'], password=auth['password']))
            return ''
        application.pull()
        return ''

    log("starting service on {host}:{port}".format(host=config['service_host'], port=config['service_port']))
    log("configuration:")
    for key in sorted(config):
        log("   {key}: {value}".format(key=key, value=config[key]))
    return rest_service.run(host=config['service_host'], port=config['service_port'], debug=config['debug'], ssl_context = context)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", help="/path/to/repo")
    args = parser.parse_args()

    config = {'app_name': 'git_mirror',
              'service_host': '0.0.0.0',
              'service_port': 8080,
              'repo_path': args.repo_path,
              'repo_remote': {'name': 'origin', 'url': 'git@github.com:afrantisak/gitmirror.git'},
              'repo_branch': 'master',
              'ssl_cert_filepath': 'test/ssl.cert',
              'ssl_key_filepath':  'test/ssl.key',
              'auth_username': 'username',
              'auth_password': 'password',
              'debug': True,
    }
    git_hook_service(config)

