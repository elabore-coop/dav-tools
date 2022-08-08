from odoo import _, api, fields, models

class Users(models.Model):
    _inherit="res.users"

    calendar_event_ids = fields.Many2many('dav.calendar', 'dav_calendar_event_user_rel', string='Dav Calendars Events')
    calendar_todo_ids = fields.Many2many('dav.calendar', 'dav_calendar_todo_user_rel', string='Dav Calendars Todo')