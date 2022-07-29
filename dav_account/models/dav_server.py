import caldav
from odoo import api, fields, models


class DavServer(models.Model):
    _name = "dav.server"
    _description = "Dav server"

    name = fields.Char('name', required=True, copy=True)
    url = fields.Char('Server url', required=True, copy=True)
    username = fields.Char('Username', required=True, copy=True)
    password = fields.Char('Password', required=True, copy=False)
    user_id = fields.Many2one('res.users', string='User', required=True, copy=True, ondelete="cascade")
    status = fields.Char(compute='_compute_status', string='Status', store=True)
    
    @api.depends("url", "username", "password")
    def _compute_status(self):
        try:
            self.get_principal()
            self.write({"status": "OK"})
        except:
            self.write({"status": "KO"})

    def get_principal(self):
        ## When using the caldav library, we start with initiating a
        ## DAVClient object, which should contain connection details and credentials.
        ## Initiating the object does not cause any requests to the server, so this
        ## will not break even if caldav url is set to example.com
        client = caldav.DAVClient(url=self.url, username=self.username, password=self.password)
        ## principal object will cause communication with the server.
        principal = client.principal()
        return principal

