# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

import logging
_logger = logging.getLogger(__name__)

class Task (models.Model):
	_inherit = 'project.task'

	resource_line_ids = fields.One2many('project_resources.resource_line', 'task_ids', string='Resources')

class Resource(models.Model):
	_inherit = 'resource.resource'

	capability_ids = fields.Many2many('project_resources.capability', string='Capabilities') # This may need more info to work.
	resource_type = fields.Selection(selection_add=[('equipment', 'Equipment')])

class ResourceLine(models.Model):
	_name = "project_resources.resource_line"
	_description = "Resource Line"

	resource_id = fields.Many2one('resource.resource', string='Resource', required=True)
	resource_type = fields.Selection('_get_resource_type_selection', compute='_get_resource_type', inverse='_set_resource_type', string='Resource Type')
	quantity = fields.Float(string='Quantity', required=True)
	cost = fields.Float(string='Cost', required=True)
	subtotal = fields.Float(string='Subtotal', compute='_get_subtotal')
	actual = fields.Float(string='Actual')
	variance = fields.Float(string='Variance', compute='_get_variance')
	task_ids = fields.Many2one('project.task')

	@api.onchange('resource_type')
	def _onchange_resource_type(self):
		res = {}
		if self.resource_type:
			res = {'domain':{'resource_id':[('resource_type','=',self.resource_type)]}}
		_logger.info(res)
		return res

	def _get_resource_type_selection(self):
		vals = self.env['resource.resource']._fields['resource_type'].selection
		return vals

	@api.depends('resource_id')
	def _get_resource_type(self):
		if self.resource_id:
			self.resource_type = self.resource_id.resource_type

	@api.depends('resource_type')
	def _set_resource_type(self):
		return

	@api.depends('quantity','cost')
	def _get_subtotal(self):
		self.subtotal = self.quantity * self.cost
		
	@api.depends('actual', 'subtotal')
	def _get_variance(self):
		self.variance = self.actual - self.subtotal

class Capability(models.Model):
	_name = "project_resources.capability"
	_description = "Capability"

	name = fields.Char('Name')
	capability_type = fields.Many2one('project_resources.capability_type', string='Type')

class CapabilityType(models.Model):
	_name = "project_resources.capability_type"
	_description = "Capability Type"

	name = fields.Char('Name')