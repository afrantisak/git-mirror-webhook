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

    def dump_config(self):
        log("configuration:")
        configkeys = vars(self.config)
        for key in sorted(configkeys):
            log("   {key}: {value}".format(key=key, value=configkeys[key]))

    def create_or_use(self):
        repo_path = self.config.repo_path
        if not os.path.exists(repo_path):
            _mkdir(repo_path)
            repo = git.Repo.init(repo_path)
        else:
            repo = git.Repo(repo_path)
        try:
            repo.remotes.origin
        except:
            name = self.config.repo_remote_name
            url = self.config.repo_remote_url
            log("creating remote {name} => {url}".format(**locals()))
            repo.create_remote(name, url)
        return repo

    def pull(self):
        origin = self.repo.remotes.origin
        log('pulling {self.config.repo_remote_url}'.format(**locals()))
        origin.pull(**{'ff-only': True})
        log('checkout {self.config.repo_branch}'.format(**locals()))
        master = self.repo.create_head('master', origin.refs.master)
        master.set_tracking_branch(origin.refs.master)
        master.checkout()
        
def git_hook_service(config):
    rest_service = flask.Flask(config.app_name)

    # load ssl certificate for https
    ssl_context = None
    if config.service_https:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.load_cert_chain(config.ssl_cert_filepath, config.ssl_key_filepath)

    # set up cross-origin resource sharing (CORS)
    cors = flask.ext.cors.CORS(rest_service, allow_headers='X-Requested-With')
    rest_service.config['CORS_HEADERS'] = 'X-Requested-With'

    application = Application(config)
    application.dump_config()
    application.pull()

    @rest_service.route("/bitbucket_commit_hook", methods=['POST'])
    @flask.ext.cors.cross_origin()
    def commit_hook():
        data = json.loads(flask.request.form['payload'])
        commits = data['commits']
        for commit in commits:
            branch = commit['branch']
            log("BRANCH: {branch}".format(**locals()))
        auth = flask.request.authorization
        if auth['username'] != config.auth_username or auth['password'] != config.auth_password:
            log("Invalid username/password: {username}/{password}".format(username=auth['username'], password=auth['password']))
            return ''
        application.pull()
        return ''

    log("starting service on {host}:{port}".format(host=config.service_host, port=config.service_port))
    return rest_service.run(host=config.service_host, port=config.service_port, debug=config.debug, ssl_context = ssl_context)

if __name__ == "__main__":
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
    args = parser.parse_args()

    git_hook_service(args)

