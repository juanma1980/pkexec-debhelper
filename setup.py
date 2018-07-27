#!/usr/bin/env python3

from setuptools import setup

if __name__ == '__main__':
	setup(name='pkexecdebhelper',
		version='0.1',
		description='Generate polkit files from config file and install',
		long_description="""""",
		author='Raul Rodrigo Segura',
		author_email='raurodse@gmail.com',
		maintainer='Raul Rodrigo Segura',
		maintainer_email='raurodse@gmail.com',
		keywords=['software','debhelper'],
		url='https://github.com/edupals/pkexec-debhelper',
		license='GPL3',
		platforms='UNIX',
		packages = ['edupals.pkexec'],
		package_dir = {'edupals.pkexec':'src'},
		scripts=['bin/dh_pkexec'],
		data_files=[('/usr/share/perl5/Debian/Debhelper/Sequence/',['Secuence/pkexec.pm']),('/usr/share/pkexec-debhelper/skel/',['templates/pkla.skel','templates/polkit.skel'])]
	)
