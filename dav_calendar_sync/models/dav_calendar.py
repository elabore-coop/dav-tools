import logging
from odoo import fields, models

_logger = logging.getLogger(__name__)

class DavCalendar(models.Model):
    _name = "dav.calendar"
    _description = "Dav calendar"

    name = fields.Char('name')
    url = fields.Char('url')
    dav_server_id = fields.Many2one('dav.server', string='Dav Server')

    sync_token = fields.Char("Synchronization Token")

    active_sync_event = fields.Boolean('active_sync_event')
    active_sync_todo = fields.Boolean('active_sync_todo')

    def _manage_timezones(self, ical_event):
        start = ical_event.get("DTSTART").dt
        end = ical_event.get("DTEND").dt
        # Odoo only uses naive dates, timezone data must be removed
        # TODO: removing timezone data is not enough, naive dates must match the user timezone
        if hasattr(start, "tzinfo"):
            start = start.replace(tzinfo=None)
        if hasattr(end, "tzinfo"):
            end = start.replace(tzinfo=None)
        return start, end

    def _existing_event(self,ical_event):
        calendar_events = self.env["calendar.event"].search([("dav_uid", "=", str(ical_event.get("UID")))])
        if len(calendar_events) > 0:
            return True
        else:
            return False   
        
    def _create_calendar_event(self, ical_event):
        start, end = self._manage_timezones(ical_event)
        values = {
            "name":str(ical_event.get("SUMMARY")),
            "start": start,
            "stop": end,
            "dav_calendar_id": self.id,
            "dav_uid" : str(ical_event.get("UID")),
        }
        self.env["calendar.event"].create(values)

    def _update_calendar_event(self, ical_event):
        calendar_event = self.env["calendar.event"].search([("dav_uid", "=", str(ical_event.get("UID")))])[0]
        start, end = self._manage_timezones(ical_event)
        values = {
            "name":str(ical_event.get("SUMMARY")),
            "start": start,
            "stop": end,
        }
        calendar_event.write(values)

    def _delete_calendar_event(self, ical_event):
        calendar_event = self.env["calendar.event"].search([("dav_uid", "=", str(ical_event.get("UID")))])[0]
        calendar_event.unlink()

    def sync_dav_events(self):
        calendar = self.dav_server_id.get_principal().calendar(self.name)
        if self.sync_token:
            dav_events = calendar.objects_by_sync_token(self.sync_token, True)
        else:
            dav_events = calendar.objects_by_sync_token(load_objects=True)
        event_created = 0
        for dav_event in dav_events:
            try:
                ical_event = dav_event.icalendar_instance.subcomponents[0]
                if dav_event.data is None:
                    self._delete_calendar_event(ical_event)
                elif self._existing_event(ical_event):
                    self._update_calendar_event(ical_event)
                else:
                    self._create_calendar_event(ical_event)
                    event_created += 1
            except Exception as e: 
                _logger.exception("SYNC FAILURE on following event: %s", dav_event.data)
                continue
        self.sync_token = dav_events.sync_token
        _logger.debug("NB EVENT CREATED: %s", event_created)