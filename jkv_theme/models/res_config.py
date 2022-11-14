
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'
    auth_signup_reset_username = fields.Boolean(string='Enable username reset from Login page', help="This allows users to trigger a username reset from the Login page.")

    @api.model
    def get_default_auth_signup_template_user_id(self, fields):
        res = super(BaseConfigSettings, self).get_default_auth_signup_template_user_id(fields)
        res.update({'auth_signup_reset_username': safe_eval(self.env['ir.config_parameter'].get_param('auth_signup.reset_username', 'False'))})
        return res


    @api.multi
    def set_auth_signup_template_user_id(self):
        super(BaseConfigSettings, self).set_auth_signup_template_user_id()
        self.env['ir.config_parameter'].set_param('auth_signup.reset_username', repr(self.auth_signup_reset_username))