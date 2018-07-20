import os
import sys
import json
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

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
        with open ('debian/${pkg}.substvars'.format(pkg),'a') as depfile:
            depfile.write('misc:Depends=' + dependency)


class PkexecDebhelper():
    def __init__(self, debhelper, debug=False):
        self.polkit_path="/usr/share/polkit-1/"
        self.polkit_path_actions = self.polkit_path + "actions"
        self.polkit_path_rules = self.polkit_path +  "rules.d"
        self.tpl_env = Environment(loader=FileSystemLoader('/usr/share/pkexec-debhelper/skel'))
        self.debug = debug
        self.debhelper = debhelper
    
    def debug_message(self, message):
        print(message)

    def process_pkexec_file(self, pkg, file_to_parse):
        with open(file_to_parse) as fd:
            configuration = json.load(fd)
            for package_conf in configuration:
                if not self.generate_polkit_rules(pkg, package_conf):
                    print('Error generating polkit files from pkexec helper')
                    sys.exit(1)
                if 'requiredx' in package_conf and package_conf['requiredx']:
                    self.debhelper.add_misc_dependency(pkg, 'xpkexec')

    def generate_polkit_rules(self, pkg, pkg_conf):
        destfolder = "debian/{pkg}.polkit.action/".format(pkg)
        pkg_conf = self.default_values_pkg_conf(pkg_conf)
        if not pkg_conf:
            return False
        if not os.path.exists(destfolder):
            os.makedirs(destfolder)
        template = self.tpl_env.get_template('polkit.skel')
        with open("{0}{1}.{2}".format(destfolder, pkg_conf['prefix'], pkg),'w') as fd:
            fd.write(template.render(pkg_conf))
        return True
    
    def generate_pkla(self, pkg, pkg_conf):
        


    def default_values_pkg_conf(self, pkg_conf):
        if not 'cmd' in pkg_conf:
            return False
        if not 'prefix' in pkg_conf:
            pkg_conf['prefix'] = "id.generic.pkexec"
        if not 'nameaction' in pkg_conf:
            pkg_conf['nameaction'] = 'genericnameaction'
        if not 'icon' in pkg_conf:
            pkg_conf['icon'] = 'noicon'
        if not 'groups' in pkg_conf:
            pkg_conf['groups'] = []
        if not 'users' in pkg_conf:
            pkg_conf['users'] = []
        return pkg_conf

