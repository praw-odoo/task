from odoo import models
from odoo.exceptions import UserError

class MailWizardInvite(models.TransientModel):
    _inherit = 'mail.wizard.invite'

    def add_followers(self):
        """
        The add_followers function adds the followers of a record to the current user.
        This is useful when you want to send a notification to all those who follow
        a document, such as a task or a project issue.
        """
        res = super().add_followers()
        # if self.env['res.users'].has_group('hr_recruitment.group_hr_recruitment_user'):
        if self.user_has_groups('hr_recruitment.group_hr_recruitment_user') and not self.user_has_groups('hr_recruitment.group_hr_recruitment_manager'):
            raise UserError(("User Group cannot add followers"))
        return res