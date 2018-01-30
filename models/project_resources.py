# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

import logging
_logger = logging.getLogger(__name__)

class Task (models.Model):
	_inherit = 'project.task'

	resource_line_ids = fields.One2many('project_resources.resource_line', 'task_id', string='Resources')
	amount_total = fields.Monetary(string="Total", compute="_get_amount_total", store=True, readonly=True)
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
		default=lambda self: self.env.user.company_id.currency_id.id)

	@api.depends('resource_line_ids.subtotal')
	def _get_amount_total(self):
		for task in self:
			total = 0.0
			for line in task.resource_line_ids:
				total += line.subtotal
			task.amount_total = total


class Project (models.Model):
	_inherit = 'project.project'

	project_cost = fields.Monetary(string="Project Budget", compute="_get_amount_total", store=True, readonly=True)
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
		default=lambda self: self.env.user.company_id.currency_id.id)

	@api.depends('task_ids.amount_total')
	def _get_amount_total(self):
		for project in self:
			total = 0.0
			for task in project.task_ids:
				total += task.amount_total
			project.project_cost = total
			

class Resource(models.Model):
	_inherit = 'resource.resource'

	capability_ids = fields.Many2many('project_resources.capability', string='Capabilities') # This may need more info to work.
	resource_type = fields.Selection(selection_add=[('equipment', 'Equipment')])
	resource_line_ids = fields.One2many('project_resources.resource_line', 'resource_id')
	cost = fields.Monetary(string='Cost Per Unit/Hour', required=True)
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
		default=lambda self: self.env.user.company_id.currency_id.id)
	# project_ids = fields.One2many()

class ResourceLine(models.Model):
	_name = "project_resources.resource_line"
	_description = "Resource Line"

	resource_id = fields.Many2one('resource.resource', string='Resource', required=True)
	resource_type = fields.Selection('_get_resource_type_selection', string='Resource Type')
	quantity = fields.Float(string='Quantity/Hours', required=True)
	cost = fields.Monetary(string='Cost', required=True)
	subtotal = fields.Monetary(string='Subtotal', compute='_get_subtotal', store=True)
	actual = fields.Float(string='Actual')
	variance = fields.Monetary(string='Variance', compute='_get_variance', store=True)
	task_id = fields.Many2one('project.task')
	currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
		default=lambda self: self.env.user.company_id.currency_id.id)

	def _domain_resource_id(self):
		dom = []
		res = {'domain':{'resource_id':dom}}

		if self.resource_type:
			# If resource type is selected, set domain to only those resources
			dom.extend(('&', ('resource_type','=',self.resource_type)))

		# Set domain to only include resources that haven't been added yet.
		resource_ids = []
		for item in self.task_id.resource_line_ids:
			item_id = item.resource_id.id
			if item_id:
				resource_ids.append(item_id)
		dom.append(('id','not in',resource_ids))

		return res

	@api.onchange('resource_id')
	def _onchange_resource_id(self):
		for rec in self:
			rec.cost = rec.resource_id.cost
			if rec.resource_id.id != False:
				_logger.info(rec.resource_id)
				rec.resource_type = rec.resource_id.resource_type
		return self._domain_resource_id()

	@api.onchange('resource_type')
	def _onchange_resource_type(self):
		for rec in self:
			if rec.resource_id and rec.resource_type != rec.resource_id.resource_type:
				rec.resource_id = False
		return self._domain_resource_id()

	# Makes sure that resource_type always has the same selection values as the resource_type field in resource.resource
	def _get_resource_type_selection(self):
		vals = self.env['resource.resource']._fields['resource_type'].selection
		return vals

	@api.depends('resource_id')
	def _get_resource_type(self):
		for rec in self:
			if rec.resource_id:
				rec.resource_type = rec.resource_id.resource_type

	@api.depends('resource_type')
	def _set_resource_type(self):
		return

	@api.depends('quantity','cost')
	def _get_subtotal(self):
		for rec in self:
			rec.subtotal = rec.quantity * rec.cost
	
	@api.depends('actual', 'subtotal')
	def _get_variance(self):
		for rec in self:
			rec.variance = rec.actual - rec.subtotal

class Capability(models.Model):
	_name = "project_resources.capability"
	_description = "Capability"

	name = fields.Char('Name')
	capability_type = fields.Many2one('project_resources.capability_type', string='Type')

class CapabilityType(models.Model):
	_name = "project_resources.capability_type"
	_description = "Capability Type"

	name = fields.Char('Name')