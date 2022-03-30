#from argparse import _MutuallyExclusiveGroup

from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit="res.partner"
