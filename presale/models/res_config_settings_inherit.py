#   coding: utf-8
##############################################################################
#
#   Copyright (C) 2022 Odoo Inc
#   Autor: Brayhan Andres Jaramillo Castaño
#   Correo: brayhanjaramillo@hotmail.com
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = "res.config.settings"

    FILTER_MODE = [("brand_only", "Por Marca")]

    filter_mode = fields.Selection(selection_add=FILTER_MODE)
