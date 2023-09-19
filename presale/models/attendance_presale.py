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


class AttendancePresale(models.Model):
    _name = "attendance.presale"
    _description = "Asistencia Preventa"
    _rec_name = "partner_id"

    partner_id = fields.Many2one("res.partner", string="Contacto")
    date = fields.Datetime("Fecha", default=fields.Datetime.now, required=True)
