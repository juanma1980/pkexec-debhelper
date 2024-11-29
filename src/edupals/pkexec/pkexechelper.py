import os
import sys
import json
import glob
from shutil import move, copy
from jinja2 import Environment
from jinja2.loaders import FileSystemLoader
import gettext
gettext.textdomain('pkexechelper')
_ = gettext.gettext

i18n={"MSG_RUN":_("Authentication is required to run")}

class PkexecDebhelper():
    def __init__(self, debug=False, audience='vendor'):
        self.polkit_path="/usr/share/polkit-1/"
        self.polkit_path_actions = self.polkit_path + "actions"
        self.polkit_path_rules = self.polkit_path +  "rules.d"
        self.polkit_path_pkla = '/var/lib/polkit-1/localauthority/'
        self.tpl_env = Environment(loader=FileSystemLoader('/usr/share/pkexec-debhelper/skel'),lstrip_blocks=True,trim_blocks=True)
        self.debug = debug
        self.audience = audience

    def debug_message(self, message):
        print(message)

    def add_misc_dependency(self, pkg, dependency):
        with open ('debian/{pkg}.substvars'.format(pkg=pkg),'a') as depfile:
            depfile.write('misc:Depends=' + dependency)

    def process_pkexec_file(self, pkg, file_to_parse):
        with open(file_to_parse) as fd:
            configuration = json.load(fd)
            for package_conf in configuration:
                package_conf = self.default_values_pkg_conf(package_conf)
                self.generate_polkit_files(pkg, package_conf)
                if package_conf['requiredx']:
                    self.add_misc_dependency(pkg, 'xpkexec')

    def generate_polkit_files(self, pkg, pkg_conf):
        self.generate_polkit_actions(pkg, pkg_conf)
        self.generate_polkit_pkla(pkg, pkg_conf)
        self.generate_polkit_rules(pkg, pkg_conf)

    def generate_polkit_actions(self, pkg, pkg_conf):
        """
            create actions files on PKG.polkit.pkla folder from configuration package
        """
        destfolder = "debian/{pkg}.polkit.action/".format(pkg=pkg)
        template = self.tpl_env.get_template('polkit.skel')
        self.exists_or_create( destfolder )
        self.save_template( pkg_conf, template, "{0}{1}.{2}".format(destfolder, pkg_conf['prefix'], pkg))

    def generate_polkit_pkla(self, pkg, pkg_conf):
        """
            create pkla files on PKG.polkit.pkla folder from configuration package
        """
        destfolder = "debian/{pkg}.polkit.pkla/".format(pkg=pkg)
        template = self.tpl_env.get_template('pkla.skel')
        self.exists_or_create( destfolder )
        self.save_template( pkg_conf, template, "{0}{1}.{2}".format(destfolder, pkg_conf['prefix'], pkg))

    def generate_polkit_rules(self, pkg, pkg_conf):
        """
            create rules files on PKG.polkit.rules folder from configuration package_conf
        """
        destfolder = "debian/{pkg}.polkit.rules/".format(pkg=pkg)
        self.exists_or_create( destfolder )
        if "rules" in pkg_conf.keys():
            for rule in pkg_conf["rules"]:
                copy( rule, destfolder)
        else:
            template = self.tpl_env.get_template('rules.skel')
            self.save_template( pkg_conf, template, "{0}{1}.{2}".format(destfolder, pkg_conf['prefix'], pkg))

    def get_not_exists_filepath(self, file_path):
        """
            Return filepath not exists adding number at the end name
        """
        counter = 0
        output_file = file_path
        while os.path.exists(output_file):
            output_file = "{0}.{1}".format(file_path, counter)
            counter = counter + 1
        return output_file

    def install_polkit_files(self, pkg):
        """
            Copy files on polkit folders
        """
        paths_polkit_files = [
            {
                'orig': 'debian/{pkg}.polkit.action'.format(pkg=pkg),
                'dest': 'debian/{pkg}/{dest}'.format(pkg=pkg,dest=self.polkit_path_actions),
                'ext' : 'policy'},
            {
                'orig': 'debian/{pkg}.polkit.rules'.format(pkg=pkg),
                'dest': 'debian/{pkg}/{dest}'.format(pkg=pkg,dest=self.polkit_path_rules),
                'ext' : 'rules' },
            {
                'orig': 'debian/{pkg}.polkit.pkla'.format(pkg=pkg),
                'dest': 'debian/{pkg}/{dest}/{audience}'.format(pkg=pkg,dest=self.polkit_path_pkla,audience=self.get_path_audience()),
                'ext' : 'pkla' }
        ]
        for element in paths_polkit_files:
            if not os.path.exists(element['orig']):
                continue
            list_files = glob.glob(os.path.join(element['orig'],'*'))
            if len(list_files) > 0:
                self.exists_or_create(element['dest'])
                for polkit_file in list_files:
                    filename = os.path.basename(polkit_file)
                    move(polkit_file, os.path.join(element['dest'],"{filename}.{ext}".format(filename=filename,ext=element['ext'])))

    def exists_or_create(self, folder):
        """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
        """
        if os.path.isdir(folder):
            pass
        elif os.path.isfile(folder):
            raise OSError("a file with the same name as the desired " \
                        "dir, '%s', already exists." % folder)
        else:
            head, tail = os.path.split(folder)
            if head and not os.path.isdir(head):
                self.exists_or_create(head)
            #print "_mkdir %s" % repr(folder)
            if tail:
                os.mkdir(folder)

    def get_path_audience(self):
        """
            Return path explained polkit-1 documentation
        """
        folder = "10-vendor.d"
        if self.audience == "org":
            folder = "20-org.d"
        if self.audience == "site":
            folder = "30-site.d"
        if self.audience == "local":
            folder = "50-local.d"
        if self.audience == "mandatory":
            folder = "90-mandatory.d"
        return folder


    def save_template(self, variables, template, dest):
        """
            Write template with on not exists file
        """
        basename=os.path.basename(".".join(variables["cmd"].split(".")[:-1]))
        if not "domain" in variables:
            variables["domain"]=basename
        if not "name" in variables:
            variables["name"]=basename
        if not "message" in variables:
            variables["message"]="{0} {1}".format(i18n.get("MSG_RUN"),basename)
        if not "description" in variables:
            variables["description"]=""
        output_file = self.get_not_exists_filepath(dest)
        with open(output_file,'w') as fd:
            fd.write(template.render(variables))

    def default_values_pkg_conf(self, pkg_conf):
        """
            Define default values for pkg configuration.
            cmd ir required
            prefix
            nameaction
            icon
            default_auth
            auths
            requiredx
        """
        if not 'cmd' in pkg_conf:
            return False
        pkg_name=os.path.basename(".".join(pkg_conf["cmd"].split(".")[:-1]))
        if not 'prefix' in pkg_conf:
            pkg_conf['prefix'] = "id.generic.pkexec"
        if not 'nameaction' in pkg_conf:
            pkg_conf['nameaction'] = 'genericnameaction'
        if not "name" in pkg_conf:
            pkg_conf["name"]=pkg_name
        if not "domain" in pkg_conf:
            pkg_conf["domain"]=pkg_name
        if not "message" in pkg_conf:
            pkg_conf["message"]="{0} {1}".format(i18n.get("MSG_RUN"),pkg_name)
        if not "description" in pkg_conf:
            pkg_conf["description"]=""
        if not 'icon' in pkg_conf:
            pkg_conf['icon'] = 'noicon'
        if not 'auths' in pkg_conf:
            pkg_conf['auths'] = []
        if not 'requiredx' in pkg_conf:
            pkg_conf['requiredx'] = False
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
