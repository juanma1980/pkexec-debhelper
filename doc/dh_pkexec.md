# dh_pkexec(1)

## SYNOPSIS
   dh_pkexec

## DESCRIPTION

## FILES
	debian/package.pkexec
		JSON similar to:

		[
			{
				"cmd": "/usr/bin/zero-center",
				"prefix": "net.lliurex.zero-center",
				"nameaction": "zero-center",
				"icon": "valentin",
				"auths": [
					{ "type":"group", "members": ["students"], "any":"no", "inactive":"no", "active":"yes"},
					{ "type":"user", "members": ["alu01"], "any":"no", "inactive":"no", "active":"yes"}
				],
				"default_auth" :{"any":"no", "inactive":"no", "active":"no" },
				"xrequired": True
			},
			{
				"cmd": "/usr/bin/zero-center-super",
				"prefix": "net.lliurex.zero-center",
				"nameaction": "zero-center",
				"icon": "valentin",
				"auths": [
					{ "type":"group", "members": ["students,teachers"], "any":"yes", "inactive":"no"},
					{ "type":"user", "members": ["alu01,alu02,alu03"], "any":"yes"},
					{ "type":"user", "members": ["alu04,alu05,alu06"], "inactive":"no"}
				],
				"default_auth" :{"any":"no", "inactive":"no", "active":"yes" }
			}
		]


	debian/package.polkit.rules/uniquename
		This file will be installed by package on rules.d polkit path 
	debian/package.polkit.action/uniquename
		This file will be installed by package on action.d polkit path 
