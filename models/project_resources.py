# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions

import logging
_logger = logging.getLogger(__name__)

class Task (models.Model):
	_inherit = 'project.task'

	resource_line_ids = fields.One2many('project_resources.resource_line', 'task_ids', string='Resources')

class ResourceLine(models.Model):
	_name = "project_resources.resource_line"
	_description = "Resource Line"

	resource_id = fields.Many2one('resource.resource', string='Resource')
	quantity = fields.Float(string='Quantity')
	cost = fields.Float(string='Cost')
	total = fields.Float(string='Total', compute='_get_total')
	actual = fields.Float(string='Actual')
	variance = fields.Float(string='Variance', compute='_get_variance')
	task_ids = fields.Many2one('project.task')


	@api.depends('quantity','cost')
	def _get_total(self):
		self.total = self.quantity * self.cost
		

	def _get_variance(self):
		result = self.actual - self.total
		return result