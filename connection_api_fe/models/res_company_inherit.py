# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    Autor: Brayhan Andres Jaramillo Castaño
#    Correo: brayhanjaramillo@hotmail.com
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import models, fields, api, exceptions
from odoo.tools.translate import _
from odoo.exceptions import Warning, UserError, ValidationError
from datetime import date, timedelta, datetime
import json

try:
    import requests
except:
    _logger.warning("no se ha cargado requests")

import logging

_logger = logging.getLogger(__name__)


class ResCompanyInherit(models.Model):

    _inherit = "res.company"

    AMBIENT = [("1", "Pruebas"), ("2", u"Producción")]

    ambient_api = fields.Selection(
        AMBIENT, string="Ambiente", default="1", required=True
    )
    url_login_api = fields.Char(
        string="URL API Login",
        help="Ingrese la Url del SETT de Pruebas o la Url del Ambiente Productivo",
    )
    email_api = fields.Char(
        string="Correo",
        help="Ingrese el email con el cual realizo el registro en la API",
    )
    password_api = fields.Char(
        string="Contraseña", help=u"Ingrese la contraseña del registro"
    )
    html_response_api = fields.Html(string="Respuesta", store=True, readonly=True)
    token_operation_api = fields.Char(
        string="Token Operación",
        store=True,
        readonly=True,
        help="Es el JWT token de seguridad.",
    )
    document_repository = fields.Char(
        string="Ruta de almacenamiento de archivos", required=True
    )

    url_import_invoice = fields.Char(
        string="Importe Facturas",
        help=u"Se utiliza para enviar los datos que se van a timbrar en la factura electrónica",
    )
    url_import_note = fields.Char(
        string="Importe Notas",
        help=u"Se utiliza para enviar los datos que se van a timbrar en la NOTA CRÉDITO.",
    )
    url_xml = fields.Char(
        string="Consumo XML",
        help=u"Se utiliza para el consumo del XML de la factura por método post",
    )
    url_pdf = fields.Char(
        string="Consumo PDF",
        help=u"Se utiliza para el consumo del PDF de la factura por método post",
    )
    report_header = fields.Html(string="Report Header")

    def return_heders_api(self):
        """
        Permite retornar los encabezados para la conexion a la API de FE
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": "Bearer token",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
            "Accept": "application/x-www-form-urlencoded",
            # "Accept": "application/x-www-form-urlencoded",
            #'Accept': '*/*',
            "Connection": "keep-alive",
            "Accept-Enconding": "gzip,deflate,br",
        }

        return headers

    def action_connect_api(self):

        if self.url_login_api and self.email_api and self.password_api:
            headers = self.return_heders_api()
            url = self.url_login_api
            data = {"email": str(self.email_api), "password": str(self.password_api)}

            write_date = self.write_date
            date_now = datetime.now()

            print(date_now)
            print(write_date)

            calculate_dates = date_now - write_date
            print(divmod(calculate_dates.total_seconds(), 60))
            calculate_minutes = int(calculate_dates.total_seconds() / 60)
            print(calculate_minutes)
            flag = True

            context = self.env.context

            if "validate_api_key" in context:
                if calculate_minutes < 55:
                    flag = False
            if flag:
                try:
                    response = requests.post(url=url, data=data, headers=headers)

                    self.html_response_api = response.text
                    if response.text:

                        value_response = json.loads(response.text)

                        vals = {
                            "html_response_api": value_response,
                        }

                        if value_response["data"]:
                            if value_response["data"]["tokenOperacion"]:
                                vals["token_operation_api"] = value_response["data"][
                                    "tokenOperacion"
                                ]

                        self.write(vals)

                except Exception as e:
                    _logger.info(e)
                    raise ValidationError(
                        "No existe comunicación con la API para el servicio de recepción de Facturas Electrónicas. Por favor, revise su red o el acceso a internet. \n Error encontrado: %s."
                        % (str(e))
                    )

        else:
            raise ValidationError(
                u"Debe diligenciar todos los campos correctamente. \n Asegurese de haber diligenciado los siguientes campos: \n -> URL API \n -> Correo \n -> Contraseña. \n Por favor, si cree que estoes un error, comuniquse con el Administrador."
            )
