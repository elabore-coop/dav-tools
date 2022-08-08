import caldav
from odoo import _, api, fields, models


class DavServer(models.Model):
    _inherit = "dav.server"

    dav_calendar_ids = fields.One2many('dav.calendar', 'dav_server_id', string='Dav Calendars')
     
    def compute_dav_calendar_ids(self):
        calendars = self.get_principal().calendars()
        for calendar in calendars:
            values = {
                "name": calendar.name,
                "url": calendar.url,
                "dav_server_id": self.id,
            }
            self.env["dav.calendar"].create(values)

