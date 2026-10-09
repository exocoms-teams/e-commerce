"""Record cron outcomes while preserving Odoo's execution behavior."""

import traceback

from odoo import models


class IrCron(models.Model):
    _inherit = "ir.cron"

    def _callback(self, cron_name, server_action_id):
        try:
            result = super()._callback(
                cron_name, server_action_id
            )
        except Exception:
            self.env["tracker.cron.log"]._log_execution_persistent(
                cron_name=cron_name,
                status="error",
                message=traceback.format_exc(),
            )
            raise

        self.env["tracker.cron.log"]._log_execution_persistent(
            cron_name=cron_name,
            status="success",
            message="Execution completed successfully.",
        )
        return result