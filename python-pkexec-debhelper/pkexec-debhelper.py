import os.path

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
    def __init__(self,debug=False):
        self.polkit_path="/usr/share/polkit-1/"
        self.polkit_path_actions = self.polkit_path + "actions"
        self.polkit_path_rules = self.polkit_path +  "rules.d"
        self.pkexec_debhelper_path = "/usr/share/pkexec-debhelper/"
        self.polkit_skel_file = self.pkexec_debhelper_path + "skel/polkit.skel"
        self.debug = debug
    
    def debug_message(self, message):
        print(message)