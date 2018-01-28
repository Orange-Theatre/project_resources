# -*- coding: utf-8 -*-
{
	'name' : 'project_resources',
	'summary' : 'Add resources(human, material, equipment) to project tasks',
	'version' : '0.1',
	'author' : 'Matthew Watkins',
	'website' : 'author_website',
	'license' : 'LGPL-3',
	'depends' : [ 'project', 'resource' ],
	'data' : [
		'views/view_project_resources.xml',
	],
	'auto_install' : False,
	'application': False,
	'installable': True,
	'qweb': [],
}
