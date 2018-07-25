import os
import sys
import json
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import glob 
class ControlParser():
    def __init__(self):
        try:
            fp = open('debian/control', 'r', encoding='utf-8')
        except IOError:
            raise Exception('cannot find debian/control file')
        self.lines = fp.readlines()
        self.packages = {}
        self.source_name = None

    def load_info(self):
        for line in self.lines:
            if line.lower().startswith('package:'):
                self.packages[line[8:].strip()] = {}
            elif line.lower().startswith('source:'):
                self.source_name = line[7:].strip()

class Debhelper():
    def add_misc_dependency(self, pkg, dependency):
        with open ('debian/${pkg}.substvars'.format(pkg=pkg),'a') as depfile:
            depfile.write('misc:Depends=' + dependency)


class PkexecDebhelper():
    def __init__(self, debhelper, debug=False, audience='vendor'):
        self.polkit_path="/usr/share/polkit-1/"
        self.polkit_path_actions = self.polkit_path + "actions"
        self.polkit_path_rules = self.polkit_path +  "rules.d"
        self.polkit_path_pkla = '/var/lib/polkit-1/localauthority/'
        self.tpl_env = Environment(loader=FileSystemLoader('/usr/share/pkexec-debhelper/skel'),lstrip_blocks=True,trim_blocks=True)
        self.tpl_env = Environment(loader=FileSystemLoader('.'),lstrip_blocks=True,trim_blocks=True)
        self.debug = debug
        self.debhelper = debhelper
        self.audience = audience
    
    def debug_message(self, message):
        print(message)

    def process_pkexec_file(self, pkg, file_to_parse):
        with open(file_to_parse) as fd:
            configuration = json.load(fd)
            for package_conf in configuration:
                package_conf = self.default_values_pkg_conf(package_conf)
                self.generate_polkit_files(pkg, package_conf)
                if 'requiredx' in package_conf and package_conf['requiredx']:
                    self.debhelper.add_misc_dependency(pkg, 'xpkexec')

    def generate_polkit_files(self, pkg, pkg_conf):
        self.generate_polkit_rules(pkg, pkg_conf)
        self.generate_polkit_pkla(pkg, pkg_conf)
        
    def generate_polkit_rules(self, pkg, pkg_conf):
        destfolder = "debian/{pkg}.polkit.action/".format(pkg=pkg)
        template = self.tpl_env.get_template('polkit.skel')
        self.exists_or_create( destfolder )
        self.save_template( pkg_conf, template, "{0}{1}.{2}".format(destfolder, pkg_conf['prefix'], pkg))
    
    def generate_polkit_pkla(self, pkg, pkg_conf):
        destfolder = "debian/{pkg}.polkit.pkla/".format(pkg=pkg)
        template = self.tpl_env.get_template('pkla.skel')
        self.exists_or_create( destfolder )
        self.save_template( pkg_conf, template, "{0}{1}.{2}".format(destfolder, pkg_conf['prefix'], pkg))

    def get_not_exists_filepath(self, file_path):
        counter = 0
        output_file = file_path
        while os.path.exists(output_file):
            output_file = "{0}.{1}".format(file_path, counter)
            counter = counter + 1
        return output_file

    def install_polkit_files(self, pkg):
        actions = glob.glob('debian/{pkg}.polkit.action/*'.format(pkg=pkg))
        if len(actions) > 0:
            self.exists_or_create(self.polkit_path_actions)

        pklas = glob.glob('debian/{pkg}.polkit.pkla/*'.format(pkg=pkg))
        if len(pklas) > 0:
            pkla_dest_folder = os.path.join(self.polkit_path_pkla,self.get_path_audience)
            self.exists_or_create(pkla_dest_folder)

    def exists_or_create(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    def get_path_audience(self):
        folder = "10.vendor.d"
        if self.audience == "org":
            folder = "20.org.d"
        if self.audience == "site":
            folder = "30.site.d"
        if self.audience == "local":
            folder = "50.local.d"
        if self.audience == "mandatory":
            folder = "90.mandatory.d"
        return folder
            

    def save_template(self, variables, template, dest):
        output_file = self.get_not_exists_filepath(dest)
        with open(output_file,'w') as fd:
            fd.write(template.render(variables))
    
    def default_values_pkg_conf(self, pkg_conf):
        if not 'cmd' in pkg_conf:
            return False
        if not 'prefix' in pkg_conf:
            pkg_conf['prefix'] = "id.generic.pkexec"
        if not 'nameaction' in pkg_conf:
            pkg_conf['nameaction'] = 'genericnameaction'
        if not 'icon' in pkg_conf:
            pkg_conf['icon'] = 'noicon'
        
        if not 'default_auth' in pkg_conf:
            if len(pkg_conf['auths']) > 0:
                pkg_conf['default_auth'] = {'any':'no' ,'inactive':'no', 'active':'no'}
            else:
                pkg_conf['default_auth'] = {'any':'yes' ,'inactive':'yes', 'active':'yes'}
        else:
            default_auth = 'no' if len(pkg_conf['auths']) > 0  else 'yes'
            if not 'any' in pkg_conf['default_auth']:
                pkg_conf['default_auth']['any'] = default_auth
            if not 'inactive' in pkg_conf['default_auth']:
                pkg_conf['default_auth']['inactive'] = default_auth
            if not 'active' in pkg_conf['default_auth']:
                pkg_conf['default_auth']['active'] = default_auth

        return pkg_conf

