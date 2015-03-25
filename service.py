#!/usr/bin/env python
import os
import sys
import git
import ssl
import time
import json
import flask
import collections

def log(text):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print("{timestamp}: {message}".format(timestamp = timestamp, message = text))

class Repository():
    @staticmethod
    def use_or_create_repo(repo_path):
        try:
            repo = git.Repo(repo_path)
        except:
            log("Repository does not exist.  Attempting to initialize new repo in {repo_path}".format(**locals()))
            repo = git.Repo.init(repo_path)
        return repo

    @staticmethod
    def use_or_create_repo_remote(repo, remote_name, remote_url):
        try:
            repo.remotes[remote_name]
        except:
            log("creating remote {remote_name} => {remote_url}".format(**locals()))
            repo.create_remote(remote_name, remote_url)

    def __init__(self, config):
        self.config = config
        self.repo = self.use_or_create_repo(self.config.repo_path)
        self.use_or_create_repo_remote(self.repo, self.config.repo_remote_name, self.config.repo_remote_url)

    def pull(self, commits = None):
        origin = self.repo.remotes.origin
        log('pulling {self.config.repo_remote_url}'.format(**locals()))
        origin.pull(**{'ff-only': True})
        log('checkout {self.config.repo_branch}'.format(**locals()))
        master = self.repo.create_head('master', origin.refs.master)
        master.set_tracking_branch(origin.refs.master)
        master.checkout()
        
def git_hook_service(config):
    log("Configuration:")
    configkeys = vars(config)
    for key in sorted(configkeys):
        log("   {key}: {value}".format(key=key, value=configkeys[key]))

    rest_service = flask.Flask(config.app_name)

    # load ssl certificate for https
    ssl_context = None
    if config.service_https:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.load_cert_chain(config.ssl_cert_filepath, config.ssl_key_filepath)

    repository = Repository(config)
    repository.pull()

    @rest_service.route("/bitbucket_commit_hook", methods=['POST'])
    def commit_hook():
        auth = flask.request.authorization
        if auth['username'] != config.auth_username or auth['password'] != config.auth_password:
            log("Invalid username/password: {username}/{password}".format(username=auth['username'], password=auth['password']))
            return ''
        data = json.loads(flask.request.form['payload'])
        commits = data['commits']
        acceptable_commits = collections.defaultdict(list)
        for commit in commits:
            acceptable = commit['author'] not in config.ignore_commits_by
            acceptable_commits[acceptable].append(commit)
            branch = commit['branch']
            author = commit['author']
            log("BRANCH: {branch}".format(**locals()))
            log("AUTHOR: {author}".format(**locals()))
        for commit in acceptable_commits[False]:
            log("IGNORING commit {node} because author is {author}".format(node=commit['node'], author=commit['author']))
        for commit in acceptable_commits[True]:
            log("accepting commit {node}".format(node=commit['node']))
        if len(acceptable_commits[True]):
            repository.pull(acceptable_commits[True])
        return ''

    log("starting service on {host}:{port}".format(host=config.service_host, port=config.service_port))
    return rest_service.run(host=config.service_host, port=config.service_port, debug=config.debug, ssl_context = ssl_context)

def main():
    defurl = 'http://github.com/afrantisak/git-mirror-webhook.git'

    import argparse
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--app-name',          default='git-mirror-webhook', help="name that flask uses")
    parser.add_argument('--service-host',      default='0.0.0.0',            help="service listen host")
    parser.add_argument('--service-port',      default=8080,                 help="service listen port")
    parser.add_argument('--service-https',     default=False,                help="service use https if True, http otherwise", action='store_true')
    parser.add_argument('--repo-path',         default='test/testrepo',      help="repo path (create if not exists)")
    parser.add_argument('--repo-remote-name',  default='origin',             help="repo remote name to checkout (create if not exists)")
    parser.add_argument('--repo-remote-url',   default=defurl,               help="repo remote url (used to create remote if not exists)")
    parser.add_argument('--repo-branch',       default='master',             help="repo branch to checkout")
    parser.add_argument('--ssl-cert-filepath', default='test/ssl.cert',      help="ssl cert filename")
    parser.add_argument('--ssl-key-filepath',  default='test/ssl.key',       help="ssl key filename")
    parser.add_argument('--auth-username',     default='username',           help="authentication username")
    parser.add_argument('--auth-password',     default='password',           help="authentication password")
    parser.add_argument('--debug',             default=False,                help="use flask debug mode", action='store_true')
    parser.add_argument('--ignore-commits-by', nargs='*',                    help="ignore commits by these authors")
    args = parser.parse_args()

    git_hook_service(args)

if __name__ == "__main__":
    sys.exit(main())
