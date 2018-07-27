# dh_pkexec(1)

## SYNOPSIS
   dh_pkexec

## DESCRIPTION
   Generate and install policykit files from configuration file. On this file set command to launch with pkexec, prefix and nameaction needed by polkit ( work as identifier ), auths definitions, default auth and if this application require X server to work.
   Auths definition is a list of dictionaries. Fields are :
  * "type": valid values are "group" or user. Define type of members
  * "members": list of members of auth
  * "any": authentication for users from other client ( SSH, XDMCP, ...)
  * "inactive": 
  * "active": autentication required for user on active X session has been display.
Values for "any", "inactive" and "active" fields has been indicated on polkit manpage
If you don't config neither "auths" not "default_auths", auths by default are "yes" for all values. If don't config default_auth but auths has been writed, default_auth for all config will be "no"

Can see example on "FILES" section

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
				"requiredx": True
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
