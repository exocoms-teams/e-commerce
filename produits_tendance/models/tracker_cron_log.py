"""Administrator-only execution logs for cron supervision."""

import logging

from odoo import SUPERUSER_ID, api, fields, models

_logger = logging.getLogger(__name__)


class TrackerCronLog(models.Model):
    _name = "tracker.cron.log"
    _description = "Cron execution log"
    _order = "execution_date desc, id desc"

    cron_name = fields.Char(string="Job", required=True)
    execution_date = fields.Datetime(
        string="Execution date",
        default=fields.Datetime.now,
        required=True,
        index=True,
    )
    status = fields.Selection(
        [
            ("success", "Success"),
            ("error", "Error"),
        ],
        string="Status",
        required=True,
        index=True,
    )
    message = fields.Text(string="Message")

    @api.model
    def log_execution(self, cron_name, status, message=None):
        """Best-effort logging within the caller's transaction."""
        if not self.env.su and not self.env.user.has_group(
            "base.group_system"
        ):
            return False

        try:
            with self.env.cr.savepoint():
                self.sudo().create({
                    "cron_name": cron_name,
                    "status": status,
                    "message": message,
                })
            return True
        except Exception:
            _logger.exception(
                "Could not record execution of %s.", cron_name
            )
            return False

    @api.model
    def _log_execution_persistent(
        self, cron_name, status, message=None
    ):
        """Keep a cron log independently of the job's transaction.

        The independent commit applies only to the log entry.
        Logging failures must not change the cron's outcome.
        """
        try:
            with self.env.registry.cursor() as log_cr:
                log_env = api.Environment(log_cr, SUPERUSER_ID, {})
                log_env["tracker.cron.log"].create({
                    "cron_name": cron_name,
                    "status": status,
                    "message": message,
                })
                log_cr.commit()
            return True
        except Exception:
            _logger.exception(
                "Could not persist execution log for %s.", cron_name
            )
            return False