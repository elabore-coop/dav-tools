from odoo import _, api, fields, models


class Meeting(models.Model):
    _inherit = 'calendar.event'

    dav_calendar_id = fields.Many2one('dav.calendar', string='Dav Calendar')
    dav_uid = fields.Char('Dav Uid', index=True)