import configparser
import yaml

from .helpers import *
from .errors import InvalidConfigError, InvalidRequirementsError


class Config:
    def __init__(self, server_url, email, password):
        self.server_url = server_url
        self.email = email
        self.password = password


class Requirement:
    def __init__(self, chart_name, version=None, file=None):
        self.chart_name = chart_name
        self.version = version
        self.file = file


def parse_config(path=None):
    config = configparser.ConfigParser()

    if not path:
        path = os.path.join(os.path.expanduser('~'), '.swing')

    if not is_readable_file(path):
        raise InvalidConfigError('Invalid config file path')
    
    with open(path, 'r') as f:
        config.read_file(f)

    if 'swing' not in config:
        raise InvalidConfigError('Config missing swing section')

    server_url = config['swing'].get('server')
    email = config['swing'].get('email')
    password = config['swing'].get('password')

    if not server_url:
        raise InvalidConfigError('Missing server url option')

    if not email:
        raise InvalidConfigError('Missing user email option')

    if not password:
        raise InvalidConfigError('Missing user password option')

    return Config(server_url, email, password)


def parse_requirements(path=None):
    if not path:
        path = get_yaml_filename(get_current_dir(), 'requirements')
                
    if not is_readable_file(path):
        raise InvalidRequirementsError(f'Invalid requirements file path ({path})')
    
    with open(path, 'r') as f:
        try:
            yaml_file = yaml.safe_load(f)
        except yaml.YAMLError:
            raise InvalidRequirementsError('Requirements are not valid yaml file')
            
    dependencies = yaml_file.get('dependencies')
    
    if not dependencies:
        raise InvalidRequirementsError('Requirements file missing dependencies attribute')

    requirements = []
    
    for d in dependencies:    
        if not d.get('name'):
            raise InvalidRequirementsError('Chart\'s name has to be specified')
        
        if not d.get('file') and not d.get('version'):
            raise InvalidRequirementsError('Release version has to be specified')
        
        if d.get('file') and not is_readable_dir(d.get('file')):
            raise InvalidRequirementsError('Chart\'s directory is not valid')
        
        requirements.append(Requirement(d.get('name'), d.get('version'), d.get('file')))
                                   
    return requirements
