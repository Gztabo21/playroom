#   coding: utf-8
##############################################################################
#
#   Copyright (C) 2021 Odoo Inc
#   Autor: Brayhan Andres Jaramillo Castaño
#   Correo: brayhanjaramillo@hotmail.com
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class L10nLatamIdentificationTypeInherit(models.Model):
    _inherit = "l10n_latam.identification.type"

    code = fields.Char(string=u"Código")
