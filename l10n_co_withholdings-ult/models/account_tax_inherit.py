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
from datetime import datetime, timedelta


class AccountTaxInherit(models.Model):
    _inherit = "account.tax"

    is_withholdings = fields.Boolean(string=u"¿Es Retención?")
    position_id = fields.Many2one(
        "account.fiscal.position", string="Account Fiscal Position"
    )
    base_taxes_ids = fields.One2many(
        "account.base.tax", "tax_id", string="Base Retenciones"
    )

    def return_dates(self):
        """
        Permite retornar la data del rango de las fechas
        """
        data = []
        dates = []

        for record in self:
            for item in record.base_taxes_ids:
                if item.is_active:
                    vals = {
                        "date_from": str(item.start_date),
                        "date_to": str(item.end_date),
                    }
                    dates.append(str(item.start_date))
                    dates.append(str(item.end_date))
                    data.append(vals)

        return {"data": data, "dates": dates}

    @api.constrains("base_taxes_ids")
    def validate_range_date(self):
        """
        Se valida que en los rangos de fechas configurados no existan fechas que interfieran en el calculo de la retencion
        """
        data_complete = self.return_dates()
        data = data_complete["data"]
        dates = data_complete["dates"]
        date_list = []

        format_date = "%Y-%m-%d"

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days) + 1):
                yield start_date + timedelta(n)

        if data:
            for x in data:
                start_date = datetime.strptime(x["date_from"], format_date)
                end_date = datetime.strptime(x["date_to"], format_date)
                for single_date in daterange(start_date, end_date):
                    date_list.append(str(single_date.strftime(format_date)))

            if date_list and dates:
                for x in dates:
                    data_new = filter(lambda index: x == index, date_list)
                    if len(list(data_new)) > 1:
                        raise UserError(
                            _(
                                "Se ha encontrado un conflicto en el rango de fechas seleccionado para %s. \n Por favor, seleccione un rango de fechas correcto."
                            )
                            % (str(x))
                        )

        return True
