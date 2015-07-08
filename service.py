#!/usr/bin/env python
import os
import sys
import ssl
import time
import flask
import collections
import json_codec
import repository
import application

def log(text):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print("{timestamp}: {message}".format(timestamp = timestamp, message = text))

def git_hook_service(config):
    log("Configuration:")
    configkeys = vars(config)
    for key in sorted(configkeys):
        log("   {key}: {value}".format(key=key, value=configkeys[key]))

    rest_service = flask.Flask(config.hook_app_name)

    # load ssl certificate for https
    ssl_context = None
    if config.service_https:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.load_cert_chain(config.ssl_cert_filepath, config.ssl_key_filepath)

    repo = repository.Repository(config)
    repo.pull()

    if config.app_cmd:
        app = application.Application(config.app_dir, config.app_cmd)
        app.restart()

    @rest_service.route("/bitbucket_commit_hook", methods=['POST'])
    def commit_hook():
        auth = flask.request.authorization
        if auth['username'] != config.auth_username or auth['password'] != config.auth_password:
            log("Invalid username/password: {username}/{password}".format(username=auth['username'], password=auth['password']))
            return ''
        data = json_codec.decode(flask.request.form['payload'])
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
        if not len(acceptable_commits[True]):
            return ''
        repo.pull(acceptable_commits[True])
        if config.app_cmd:
            app.restart()
        return ''

    log("starting service on {host}:{port}".format(host=config.service_host, port=config.service_port))
    ret = rest_service.run(host=config.service_host, port=config.service_port, debug=config.debug, 
                            ssl_context=ssl_context, use_reloader=False)
    app.stop()
    return ret

def main():
    defurl = 'http://github.com/afrantisak/git-mirror-webhook.git'

    import argparse
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--hook-app-name',     default='git-mirror-webhook', help="name that flask uses")
    parser.add_argument('--service-host',      default='0.0.0.0',            help="service listen host")
    parser.add_argument('--service-port',      default=8080,  type=int,      help="service listen port")
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
    parser.add_argument('--ignore-commits-by', nargs='*', default=[],        help="ignore commits by these authors")
    parser.add_argument('--app-dir',           default='test/testrepo',      help="application working dir")
    parser.add_argument('--app-cmd',           default=None,                 help="application command line")
    args = parser.parse_args()

    git_hook_service(args)

if __name__ == "__main__":
    sys.exit(main())
