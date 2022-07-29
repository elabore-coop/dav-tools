from odoo import _, api, fields, models

class Users(models.Model):
    _inherit="res.users"

    dav_server_ids = fields.One2many('dav.server', 'user_id', string='Dav Server')