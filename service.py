#!/usr/bin/env python
import os
import git
import ssl
import flask
import flask.ext
import flask.ext.cors
import requests
import json

def log(text):
    timestamp = time.strftime("%Y-%M-%d %H:%m:%S")
    print("{timestamp}: {message}".format(timestamp = timestamp, message = text))

class Application():
    def __init__(self, config):
        self.config = config
        self.repo = git.Repo(config['repo_path'])

    def pull(self):
        log('pull from {repo_path} starting'.format(repo_path=config['repo_path']))
        self.repo.remotes.origin.pull(**{'ff-only': True})
        log('pull from {repo_path} complete'.format(repo_path=config['repo_path']))

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
        data = lib.codec.decode(flask.request.data)
        auth = flask.request.authorization
        if auth['username'] != config['username'] or auth['password'] != config['password']:
            log("Invalid username/password: {username}/{password}".format(username=auth['username'], password=auth['password']))
            return ''
        application.fetch()
        return ''

    log("starting service on {host}:{port}".format(host=config['host'], port=config['port']))
    log("configuration:")
    for key in config:
        log("   {key}: {value}".format(key=key, value=config['key']))
    return rest_service.run(host=config['host'], port=config['port'], debug=True, ssl_context = context)

def bitbucket_hook_test(url = "https://user:password@localhost:8080/commit_hook"):
    data = {
        "canon_url": "https://bitbucket.org",
        "commits": [
            {
                "author": "marcus",
                "branch": "master",
                "files": [
                    {
                        "file": "somefile.py",
                        "type": "modified"
                    }
                ],
                "message": "Added some more things to somefile.py\n",
                "node": "620ade18607a",
                "parents": [
                    "702c70160afc"
                ],
                "raw_author": "Marcus Bertrand <marcus@somedomain.com>",
                "raw_node": "620ade18607ac42d872b568bb92acaa9a28620e9",
                "revision": None,
                "size": -1,
                "timestamp": "2012-05-30 05:58:56",
                "utctimestamp": "2012-05-30 03:58:56+00:00"
            }
        ],
        "repository": {
            "absolute_url": "/marcus/project-x/",
            "fork": False,
            "is_private": True,
            "name": "Project X",
            "owner": "marcus",
            "scm": "git",
            "slug": "project-x",
            "website": "https://atlassian.com/"
        },
        "user": "marcus"
    }
    result = requests.post(url, data = json.dumps(data), verify=False)
    print result.text

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_path", help="/path/to/repo")
    parser.add_argument("--test-bitbucket-commit-hook", help = "post sample bitbucket commit hook data to this url")
    args = parser.parse_args()

    if args.test_bitbucket_commit_hook:
        bitbucket_hook_test(args.test_bitbucket_commit_hook)
    else:
        config = {'app_name': 'git_mirror',
                  'host': '0.0.0.0',
                  'port': 8080,
                  'repo_path': args.repo_path,
                  'ssl_cert_filepath': 'credentials/ssl.cert',
                  'ssl_key_filepath':  'credentials/ssl.key',
                  'username': 'whytehmg',
                  'password': 'griffey24',
        }
        git_hook_service(config)

