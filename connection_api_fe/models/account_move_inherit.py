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
import json
from babel.dates import format_datetime, format_date
from odoo.tools.misc import formatLang, format_date, get_lang
from collections import defaultdict
from num2words import num2words

import logging

_logger = logging.getLogger(__name__)

from datetime import datetime, timedelta, date, timezone
import csv
import os
import io

import qrcode
from io import BytesIO

try:
    import requests
except:
    _logger.warning("no se ha cargado requests")
try:
    import base64
except ImportError:
    _logger.warning("Cannot import base64 library *****************************")
try:
    import gzip
except:
    _logger.warning("no se ha cargado gzip ***********************")

import zipfile

try:
    import re
except ImportError:
    _logger.warning("Cannot import re library")
try:
    import zlib

    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

try:
    import pyqrcode
except ImportError:
    _logger.warning("Cannot import pyqrcode library ***************************")

try:
    import png
except ImportError:
    _logger.warning("Cannot import png library ********************************")


class AccountMoveInherit(models.Model):

    _inherit = "account.move"

    STATE_DIAN = [
        ("por_notificar", "Por notificar"),
        ("error", "Error"),
        ("to_validate", "Por validar"),
        ("exitoso", "Exitoso"),
        ("rechazado", "Rechazado"),
    ]

    DOCUMENT_TYPE_DIAN = [("f", "Factura"), ("c", "Nota/Credito"), ("d", "Nota/Debito")]

    TYPE_NOTE_CREDIT = [
        (
            "1",
            "Devolución de parte de los bienes; no aceptación de partes del servicio",
        ),
        ("2", "Anulación de factura electrónica"),
        ("3", "Rebaja total aplicada"),
        ("4", "Descuento total aplicado"),
        ("5", "Rescisión: Nulidad por falta de requisitos"),
        ("6", "Otros"),
    ]

    def _default_payment_method_dian(self):
        """
        Permite cargar el tributo por defecto en el tercero
        """
        payment_method_id = self.env["payment.methods.dian"].search(
            [("code", "=", "10")], limit=1
        )
        if payment_method_id:
            return (
                self.env["payment.methods.dian"]
                .search([("code", "=", "10")], limit=1)
                .id
            )

    def _total_amount_discount(self):
        for record in self:
            discount = sum(
                (line.price_unit - line.price_subtotal)
                for line in record.invoice_line_ids
            )
            if discount < 0:
                discount = 0
            record.amount_discount = discount

    @api.depends("amount_total")
    def amount_to_words(self):

        self.text_amount = str(
            num2words(
                self.amount_total,
                to="currency",
                lang="es_CO",
            )
        ).upper()

    amount_discount = fields.Float(
        string="Total Descuento", digits="Discount", compute="_total_amount_discount"
    )
    text_amount = fields.Char(string="Monto en Letras", compute="amount_to_words")
    state_dian = fields.Selection(
        STATE_DIAN,
        string="Estado Documento Dian",
        readonly=True,
        default="por_notificar",
        store=True,
        copy=False,
    )
    document_type_dian = fields.Selection(
        DOCUMENT_TYPE_DIAN,
        string="Tipo de documento",
        readonly=True,
        store=True,
        default="f",
        copy=False,
    )
    xml_file_name = fields.Char(
        string="Nombre archivo xml", readonly=True, store=True, copy=False
    )
    xml_file = fields.Binary(
        string="Documento XML",
        help="Permite descargar el documento xml para la DIAN",
        readonly=True,
        store=True,
        copy=False,
        attachment=False,
    )
    zip_file_name = fields.Char(
        string="Nombre archivo zip",
        readonly=True,
        store=True,
        copy=False,
    )
    zip_file = fields.Binary(
        string="Archivo zip",
        help="Permite descargar el arhivo zip",
        readonly=True,
        store=True,
        copy=False,
        attachment=False,
    )
    pdf_file_save = fields.Char(
        string="Nombre archivo PDF",
        store=True,
        copy=False,
    )
    pdf_file_name = fields.Char(
        string="Nombre archivo PDF",
        readonly=True,
        store=True,
        copy=False,
    )
    pdf_file = fields.Binary(
        string="Documento PDF",
        help="Permite descargar el arhivo PDF",
        readonly=True,
        store=True,
        copy=False,
        attachment=False,
    )
    QR_code = fields.Binary(
        string="Código QR",
        readonly=True,
        store=True,
        copy=False,
        attachment=False,
    )
    cufe = fields.Char(
        string="CUFE",
        readonly=True,
        store=True,
        copy=False,
    )
    xml_response_dian = fields.Html(
        string="Contenido XML de la respuesta DIAN",
        readonly=True,
        store=True,
        copy=False,
    )
    payment_method_dian_id = fields.Many2one(
        "payment.methods.dian",
        string="Métodos de Pago DIAN",
        default=_default_payment_method_dian,
        copy=False,
    )

    xml_response = fields.Html(
        string="JSON",
        readonly=True,
        store=True,
        copy=False,
        placeholder="Se mostrara el json que es generado para enviarlo a la DIAN",
    )
    type_note_credit = fields.Selection(
        TYPE_NOTE_CREDIT,
        string="Motivo Nota Crédito",
        default="6",
        copy=False,
    )
    notes_fe = fields.Text(
        string="Notas Facturación",
        copy=False,
    )

    guide_number = fields.Char(
        string="Nº de Guía",
        copy=False,
    )

    resolution_number = fields.Char(
        "Resolution number in invoice",
        copy=False,
    )
    resolution_date = fields.Date(
        string="Resolution Date",
        copy=False,
    )
    resolution_date_to = fields.Date(
        string="Resolution Date To",
        copy=False,
    )
    resolution_number_from = fields.Integer(
        string="Resolution Number From",
        copy=False,
    )
    resolution_number_to = fields.Integer(
        string="Resolution Number To",
        copy=False,
    )
    response_api = fields.Text(string="Respuesta Api", copy=False, readonly=True)

    def action_post(self):
        """
        Funcion que permite guardar los datos de la resolucion de la factura cuando esta es confirmada
        """
        for inv in self:
            sequence = self.env["ir.sequence.dian_resolution"].search(
                [
                    ("sequence_id", "=", self.journal_id.secure_sequence_id.id),
                    ("active_resolution", "=", True),
                ],
                limit=1,
            )

            inv.resolution_number = sequence["resolution_number"]
            inv.resolution_date = sequence["date_from"]
            inv.resolution_date_to = sequence["date_to"]
            inv.resolution_number_from = sequence["number_from"]
            inv.resolution_number_to = sequence["number_to"]

        result = super(AccountMoveInherit, self).action_post()

        # self.validate_dian()
        return result

    def show_json_data_fe(self):
        self.validate_fields_invoice_fe()
        data = self.return_data_dian()

        if data:
            self.xml_response = data
        else:
            self.xml_response = "No se ha encontrado resultados"

    def return_partner_invoice(self):
        partner_id = self.partner_id
        if partner_id:
            if partner_id.parent_id:
                partner_id = partner_id.parent_id
        return partner_id

    def action_invoice_open(self):
        res = super(AccountMoveInherit, self).action_invoice_open()
        self.write({"state_dian": "to_validate"})
        return res

    @api.model
    def _generate_files_name(self):
        """
        Retorna el nombre del attached document
        """
        prefix = self.return_prefix_name_file()
        partner_id = self.return_partner_invoice()
        nit = str((partner_id.vat))
        ppp = "000"
        aa = str(fields.Date.context_today(self))[2:4]  # anio actual
        dddddddd = str(self.env["ir.sequence"].next_by_code("connection.api.fe.number"))
        # xidentification.zfill(10)
        file_name_xml = prefix + nit + ppp + aa + dddddddd + ".xml"
        file_attached_xml = "ad" + nit + ppp + aa + dddddddd + ".xml"
        zip_file_name = "z" + nit + ppp + aa + dddddddd + ".zip"

        vals = {
            "xml": file_name_xml,
            "attached": file_attached_xml,
            "zip": zip_file_name,
            "pdf": file_name_xml,
        }

        return vals

    def IntToHex(self, dian_code_int):
        dian_code_hex = "%02x" % dian_code_int
        return dian_code_hex

    def return_storage_file_invoice_dian(self):
        """
        Permite retornar la ruta de almacenamiento de los archivos generados en la consulta con la API
        """
        company = self.env.company
        if company.document_repository:
            return company.document_repository
        else:
            raise ValidationError(
                "Para poder almacenar los Documentos de la Dian. Debe de definir una ruta de almacenamiento en la compañia."
            )

    def create_attachment_document_dian(self, file_name, data_xml):
        """
        Permite crear un archivo adjunto en la factura
        """
        dian_xml = base64.b64encode(data_xml)
        rs_adjunto = self.env["ir.attachment"].sudo()
        dictAdjunto = {
            "name": file_name,
            "res_id": self.id,
            "res_model": "account.move",
            # "res_model_name": "Factura",
            "res_field": None,
            "mimetype": "application/xml;charset=utf-8",
            "public": False,
            # "datas_fname": file_name,
            # "res_name": file_name,
            "datas": dian_xml,
            "type": "binary",
        }
        nuevo_adjunto = rs_adjunto.create(dictAdjunto)

    def _return_pdf_api(self, response, file_name):
        """
        Permite generar el archivo pdf en la ruta indicada, como tambien lo asigna como adjunto
        """

        if response:
            if "pdf_base64" in response:

                file_name = file_name.replace(".xml", ".pdf")
                ruta_pdf = self.return_storage_file_invoice_dian() + "/" + file_name

                pdf_string = response["pdf_base64"]
                with open(os.path.expanduser(ruta_pdf), "wb") as fout:
                    fout.write(base64.decodebytes(pdf_string.encode("ascii")))

                data_xml = open(ruta_pdf, "rb")
                data_xml = data_xml.read()
                contenido_data_xml_b64 = base64.b64encode(data_xml)
                contenido_data_xml_b64 = contenido_data_xml_b64.decode()

                self.pdf_file_save = pdf_string
                self.pdf_file = contenido_data_xml_b64
                self.pdf_file_name = file_name

    def save_pdf_file(self, file_name):

        pdf_string = self.pdf_file_save

        if pdf_string:
            file_name = file_name.replace(".xml", ".pdf")
            ruta_pdf = self.return_storage_file_invoice_dian() + "/" + file_name
            # _logger.info("la ruta completa es: " + str(ruta_pdf))

            with open(os.path.expanduser(ruta_pdf), "wb") as fout:
                fout.write(base64.decodebytes(pdf_string.encode("ascii")))

            data_xml = open(ruta_pdf, "rb")
            data_xml = data_xml.read()
            contenido_data_xml_b64 = base64.b64encode(data_xml)
            contenido_data_xml_b64 = contenido_data_xml_b64.decode()

            self.pdf_file = contenido_data_xml_b64
            self.pdf_file_name = file_name

    def _generate_xml_file(self, file_name, document_repository, data_xml_document):
        """
        Permite generar el archivo .xml en la ruta indicada, como tambien lo asigna como adjunto
        """
        xml_file = document_repository + "/" + file_name

        data_xml = xml_file

        f = open(data_xml, "w")
        f.write(str(data_xml_document))
        f.close()

        data_xml = open(data_xml, "rb")
        data_xml = data_xml.read()
        contenido_data_xml_b64 = base64.b64encode(data_xml)
        contenido_data_xml_b64 = contenido_data_xml_b64.decode()
        self.xml_file = contenido_data_xml_b64
        self.xml_file_name = file_name

    def _generate_zip_file(self, FileNameZIP, FileNameXML, document_repository):
        """
        Permite generar el archivo .zip en la ruta indicada, como tambien lo asigna como adjunto
        """

        # Comprime archvio XML
        zip_file = document_repository + "/" + FileNameZIP
        xml_file = document_repository + "/" + FileNameXML
        pdf_file = xml_file
        pdf_64 = self.create_attachment_temp()

        object_name = pdf_file.replace(".xml", ".pdf")
        object_open = open(object_name, "wb")
        object_open.write(pdf_64)
        object_open.close()

        zf = zipfile.ZipFile(zip_file, mode="w")

        try:
            zf.write(xml_file, compress_type=compression)
            zf.write(object_name)
        finally:
            zf.close()
        # Obtiene datos comprimidos
        data_xml = zip_file
        data_xml = open(data_xml, "rb")
        data_xml = data_xml.read()
        contenido_data_xml_b64 = base64.b64encode(data_xml)
        contenido_data_xml_b64 = contenido_data_xml_b64.decode()
        self.zip_file = contenido_data_xml_b64
        self.zip_file_name = FileNameZIP

        # if self.move_type != 'out_refund':

        return contenido_data_xml_b64

    def generate_files_document_dian(self, value_response):
        """
        Permite generar los archivos de .xml y .zip en la ruta indicada
        """
        xml_dian = self.get_xml_dian(value_response)

        data_xml_document = xml_dian
        data_file_name = self._generate_files_name()
        FileNameXML = data_file_name["xml"]  # Nombre .xml
        FileNameZIP = data_file_name["zip"]  # nombre .zip

        document_repository = self.return_storage_file_invoice_dian()

        try:
            self.QR_code = self.get_qr_dian(value_response)
        except Exception as e:
            _logger.info(e)

        self._return_pdf_api(value_response, FileNameXML)
        self._generate_xml_file(FileNameXML, document_repository, data_xml_document)
        zip_xml = self._generate_zip_file(FileNameZIP, FileNameXML, document_repository)
        self.enviar_email(zip_xml, FileNameZIP)
        # self._return_pdf_api(value_response, FileNameXML)
        self.save_pdf_file(FileNameXML)

    def return_date_format(self, date_format):
        """
        Permite retornar la fecha en formato unix
        """
        date_fixed = ""
        if date_format:
            month = date_format.month
            year = date_format.year
            day = date_format.day
            dt = datetime(year, month, day)
            timestamp = dt.replace(tzinfo=timezone.utc).timestamp()

            format = "%Y-%m-%d %H:%M:00"
            now = fields.Datetime.context_timestamp(
                self, fields.Datetime.from_string(fields.Datetime.now())
            )
            fecha = now + timedelta(hours=-5)
            date_fixed = str(date_format) + " " + str(str(fecha)[11:19])

        return str(date_fixed)

    def type_voucher(self):
        """
        Tipo de comprobante
        """
        return {
            "INVOIC": "Factura",
            "NC": "Nota Crédito",
            "ND": "Nota Débito",
        }

    def return_type_voucher(self):
        """
        Permite retornar la clave del tipo de comprobante
        """
        if self.move_type == "out_invoice":
            return "INVOIC"
        if self.move_type == "out_refund":
            return "NC"  # factura rectificativa
        if self.move_type == "in_invoice":  # factura proveedor
            pass
        if self.move_type == "in_refund":  # factura rectificativa proveedor
            return "ND"

    def return_prefix_name_file(self):
        """
        Permite retornar el prefijo para la factura
        fv -> Factura de venta
        nc -> Nota credito
        nd -> Nota debito
        """
        if self.move_type == "out_invoice":
            return "fv"
        if self.move_type == "out_refund":
            return "nc"
        if self.move_type == "in_invoice":  # factura proveedor
            pass
        if self.move_type == "in_refund":  # factura rectificativa
            return "nd"

    def type_invoice_fe(self):
        """
        Tipo de documento fe
        NIU	número de unidades internacionales
        """
        return {
            "01": "FACTURA DE VENTA",
            "02": "FACTURA DE EXPORTACIÓN",
            "03": "FACTURA DE CONTINGENCIA FACTURADOR",
            "91": "NOTA DE CREDITO",
            "92": "NOTA DE DEBITO",
        }

    def return_prefix_invoice_dian(self):
        """
        Permite retornar el prefijo de la factura
        """
        if self.journal_id:
            return self.journal_id.secure_sequence_id.prefix
        return ""

    def return_prefix_invoice_notes_dian(self):
        """
        Permite retornar el prefijo de la factura de notas
        """
        if self.sequence_prefix:
            return self.sequence_prefix
        return ""

    def return_prefix_invoice_dian_notes(self):
        """
        Permite retornar el prefijo de la factura
        """
        if self.sequence_prefix:
            return self.sequence_prefix
        return ""

    def return_number_invoice_dian(self):
        """
        Permite retornar el numero de la factura
        """
        prefix = self.return_prefix_invoice_dian()
        size_prefix = len(prefix)
        number_invoice = None
        if size_prefix > 0:
            number_invoice = str(self.name)[size_prefix:]

        return str(int(number_invoice))

    def return_number_invoice_dian_notes(self):
        """
        Permite retornar el numero de la factura de notas
        """
        return self.sequence_number

    def validate_unit_measure_products(self):
        """
        Permite retornar un string con los productos que no tengan configurado la unidad de medida
        """
        message = ""
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                if line.product_id:
                    if not line.product_id.unit_measure_id:
                        message += (
                            "El producto %s debería de tener configurado la Unidad de Medida. \n"
                            % (line.name)
                        )
        return message

    def get_partner_fiscal_responsability_code(self, partner_id):
        """
        Permite retornar las responsabilidades del tercero cada una de ellas separadas por un ;
        """
        fiscal_responsability_codes = ""

        if partner_id:
            for fiscal_responsability in partner_id.fiscal_responsability_ids:
                fiscal_responsability_codes += (
                    ";" + fiscal_responsability.code
                    if fiscal_responsability_codes
                    else fiscal_responsability.code
                )

        return fiscal_responsability_codes

    def return_type_invoice_dian(self):
        """
        Permite retornar el tipo de factura
        """
        if self.move_type == "out_invoice":
            return "01"
        if self.move_type == "out_refund":
            return "91"
        if self.move_type == "in_invoice":  # factura proveedor
            pass
        if self.move_type == "in_refund":  # factura rectificativa
            return "92"

    def validate_fields_invoice_fe(self):
        """
        Permite retornar un string con los errores encontrados en la validacion para enviar los datos a la fe
        """
        message = self.validate_unit_measure_products()
        if self.partner_id:
            partner_id = self.return_partner_invoice()

            if not partner_id.l10n_latam_identification_type_id.id != 1:
                message += (
                    "El tercero debería de tener un Tipo de Identificación valido. \n"
                )
            if not partner_id.vat:
                message += "El tercero debería de tener un Número de identificación. \n"
            if not partner_id.street:
                message += "El tercero debería de tener una Dirección asociada. \n"
            if not partner_id.city_id:
                message += "El tercero debería de tener una Ciudad asociada. \n"
            if not partner_id.email:
                message += "El tercero debería de tener un Correo asociado. \n"
            if not self.get_partner_fiscal_responsability_code(partner_id):
                message += "El tercero debería de tener por lo menos una Responsabilidad Fiscal asociada. \n"

        if len(message) > 0:
            raise ValidationError(message)

    def return_value_tax_dian(self, line):
        """
        Permite retornar el tipo de impuesto que fue asociado al impuesto
        """
        if line:
            if line.tax_ids:
                for x in line.tax_ids:
                    if x.validate_dian:
                        if x.type_tax_dian:
                            return {"type_tax": x.type_tax_dian, "amount_tax": x.amount}
        # raise ValidationError('Dede de configurar por lo menos un impuesto')

    def return_type_person_dian(self):
        """
        Permite retornar el tipo de persona, ya que en la API esta trocado este valor
        """
        partner_id = self.return_partner_invoice()
        if partner_id:
            personType = partner_id.personType
            if personType == "1":
                return 2
            if personType == "2":
                return 1

    def return_tax_retention(self, retention):
        """
        Permite retornar la retencion de la factura
        """
        amount = None
        percent = None
        data = self.load_line_tax_ids()

        for record in data:
            if record.get("taxes", False):
                for tax in record.get("taxes"):
                    if tax.get("type_tax_dian") == retention:
                        amount = tax.get("tax_amount")
                        percent = tax.get("amount")

        # if self.tax_line_ids:
        #     for x in self.tax_line_ids:
        #         if x.tax_id.type_tax_dian == retention:
        #             amount = x.amount_total
        #             percent = x.tax_id.amount
        return {"amount": amount, "percent": percent}

    def returnNotes(self):
        message = ""
        if self.guide_number:
            message += str(self.guide_number)
        return message

    def return_number_lines(self):
        """
        Permite retornar la cantidad de lineas que tiene la factura
        """
        total_lineas = 0
        for record in self.invoice_line_ids:
            if record.product_id:
                total_lineas += 1

        return total_lineas

    def return_picking_name_so(self):
        """
        Permite retornar el picking
        """
        name_pickings = ""
        if self.invoice_origin:
            sale_order_ids = self.env["sale.order"].search(
                [("name", "in", self.invoice_origin.split(", "))]
            )
            if sale_order_ids:
                picking_ids = self.env["stock.picking"].search(
                    [("sale_id", "in", sale_order_ids.ids)]
                )
                if picking_ids:
                    for x in picking_ids:
                        name_pickings += x.name + ", "
        return name_pickings

    def return_name_so(self):
        """
        Permite retornar el so
        """
        name_so = ""
        if self.invoice_origin:
            sale_order_ids = self.env["sale.order"].search(
                [("name", "in", self.invoice_origin.split(", "))]
            )
            if sale_order_ids:
                for x in sale_order_ids:
                    name_so += x.name + ", "
        return name_so

    def return_partner_shipping_street(self):
        street = ""
        if self.partner_shipping_id:
            street = self.partner_shipping_id.street
        return street

    def return_partner_ref(self):
        """
        Permite retornar partener ref
        """
        partner_ref = ""
        if self.invoice_origin:
            sale_order_ids = self.env["sale.order"].search(
                [("partner_ref", "in", self.invoice_origin.split(", "))]
            )
            if sale_order_ids:
                for x in sale_order_ids:
                    partner_ref += x.name + ", "
        return partner_ref

    def return_partner_shipping(self):
        partner_shipping_id = self.partner_shipping_id
        name_shipping = ""
        if partner_shipping_id:
            name_shipping = "%s %s %s" % (
                (partner_shipping_id.street or ""),
                (partner_shipping_id.street2 or ""),
                partner_shipping_id.name,
            )
        return name_shipping

    def return_type_transaction(self):
        payment_term_id = self.invoice_payment_term_id
        data_payment_term_id = self.env.ref("account.account_payment_term_immediate")

        type_transaction = "1"
        if data_payment_term_id:
            if payment_term_id.id != data_payment_term_id.id:
                type_transaction = "2"
        return type_transaction

    def return_structure_data_line_invoice(self, line):
        """
        Permite retornar un diccionario con la informacion de la linea de factura
        """
        partner_id = self.partner_id
        display_name = partner_id.display_name

        street = ""
        name_shipping = self.return_partner_shipping()
        type_transaction = self.return_type_transaction()

        if partner_id.street:
            street = partner_id.street + " "
        if partner_id.street2:
            street += partner_id.street2

        if partner_id:
            if partner_id.parent_id:
                partner_id = partner_id.parent_id

        tax = self.return_value_tax_dian(line)
        product_id = line.product_id

        xidentification = ""
        if partner_id.l10n_latam_identification_type_id.code == "31":
            xidentification = str(partner_id.vat).replace(".", "")
        else:
            xidentification = partner_id.vat

        rte_iva = self.return_tax_retention("05")
        rte_fuente = self.return_tax_retention("06")
        rte_ica = self.return_tax_retention("07")

        seller_identification = ""
        seller = ""
        if line.move_id.invoice_user_id:
            if line.move_id.invoice_user_id.partner_id.vat:
                seller_identification = line.move_id.invoice_user_id.partner_id.vat
            seller = (
                seller_identification
                + "-"
                + line.move_id.invoice_user_id.partner_id.name
            )

        vals = {
            "LetraFactura": self.return_prefix_invoice_dian(),
            "ResolucionFacturacionElectronica": self.resolution_number,
            "Documento": self.return_number_invoice_dian(),
            "Identificacion": xidentification,
            "TipoDocumento": partner_id.l10n_latam_identification_type_id.code,
            "TipoPersona": self.return_type_person_dian(),
            "RazonSocial": display_name,
            "NombreComercial": partner_id.ref or partner_id.display_name,
            # "Direccion": street,
            "Direccion": name_shipping,
            "Ciudad": partner_id.city_id.code,
            "Telefono": (partner_id.mobile or partner_id.phone) or "",
            "Correo": partner_id.email,
            "TipoResponsabilidad": self.get_partner_fiscal_responsability_code(
                partner_id
            ),
            "FechaTransaccionCartera": self.return_date_format(self.invoice_date),
            "Porcentaje_RTE_FUENTE": rte_fuente["percent"],
            "RTE_FUENTE": rte_fuente["amount"],
            "Porcentaje_RTE_IVA": rte_iva["percent"],
            "RTE_IVA": rte_iva["amount"],
            "Porcentaje_RTE_ICA": rte_ica["percent"],
            "RTE_ICA": rte_ica["amount"],
            "TipoComprobante": self.return_type_voucher(),
            "TipoFactura": self.return_type_invoice_dian(),
            "TipoMoneda": "COP",
            "FechaVencimiento": self.return_date_format(self.invoice_date_due),
            "Notas": self.notes_fe or "",
            # "TipoTransaccion": str(self.payment_method_dian_id.name).upper(),
            "TipoTransaccion": type_transaction,
            "TipoMedioPago": self.payment_method_dian_id.code,
            "IdProductoServicio": product_id.id,
            "CantidadProductoServicio": str(line.quantity),
            "NombreProductoServicio": str(line.product_id.name)
            .replace('"', "")
            .replace("'", ""),
            "TipoUnidadMedidaProductoServicio": product_id.unit_measure_id.code,
            "InfoAdicionalProductoServicio": line.product_id.code_cum
            if line.product_id.code_cum
            else "",
            "ValorProductoServicio": str(line.price_unit),
            "TipoImpuesto": tax["type_tax"] if tax else "",
            "ValorImpuesto": tax["amount_tax"] if tax else "",
            "Porcentaje_Dcto": line.discount or 0,
            "Descripcion_Dcto": "SIN DESCUENTO",
            "ActualizarProducto": "NO",
            "guia_envio": self.return_partner_shipping_street()
            + " "
            + self.returnNotes(),
            "p_publico": str(0),
            "vendedor": str(seller),
            "numero_lineas": self.return_number_lines(),
            "remision": self.return_name_so(),
            # "remision": self.return_picking_name_so(),
            "TipoOperacion": "20",
        }

        return vals

    def return_structure_data_line_notes(self, line):
        """
        Permite retornar un diccionario con la informacion de la linea de factura para las notas creditos o debitos
        """
        partner_id = self.partner_id
        display_name = partner_id.display_name

        street = ""

        name_shipping = self.return_partner_shipping()

        if partner_id.street:
            street = partner_id.street + " "
        if partner_id.street2:
            street += partner_id.street2

        if partner_id:
            if partner_id.parent_id:
                partner_id = partner_id.parent_id

        type_transaction = self.return_type_transaction()

        tax = self.return_value_tax_dian(line)
        product_id = line.product_id

        xidentification = ""
        if partner_id.l10n_latam_identification_type_id.code == "31":
            xidentification = str(partner_id.vat).replace(".", "")
        else:
            xidentification = partner_id.vat

        rte_iva = self.return_tax_retention("05")
        rte_fuente = self.return_tax_retention("06")
        rte_ica = self.return_tax_retention("07")

        seller_identification = ""
        seller = ""
        if line.move_id.invoice_user_id:
            if line.move_id.invoice_user_id.partner_id.vat:
                seller_identification = line.move_id.invoice_user_id.partner_id.vat
            seller = (
                seller_identification
                + "-"
                + line.move_id.invoice_user_id.partner_id.name
            )

        if not self.type_note_credit:
            raise ValidationError(
                "Asegurese de haber elegido un motivo de la nota crédito."
            )

        type_operation = 20
        if not self.ref:
            type_operation = 22
        vals = {
            "LetraNota": self.return_prefix_invoice_dian_notes(),
            "ResolucionNotaElectronica": self.resolution_number,
            "Documento": self.return_number_invoice_dian_notes(),
            "numeroFactura": self.invoice_origin if self.invoice_origin else self.name,
            "Identificacion": xidentification,
            "TipoDocumento": partner_id.l10n_latam_identification_type_id.code,
            "TipoPersona": self.return_type_person_dian(),
            "RazonSocial": display_name,
            "NombreComercial": partner_id.ref or partner_id.display_name,
            # "Direccion": street,
            "Direccion": name_shipping,
            "Ciudad": partner_id.city_id.code,
            "Telefono": (partner_id.mobile or partner_id.phone) or "",
            "Correo": partner_id.email,
            "TipoResponsabilidad": self.get_partner_fiscal_responsability_code(
                partner_id
            ),
            "FechaTransaccionCartera": self.return_date_format(self.invoice_date),
            "Porcentaje_RTE_FUENTE": rte_fuente["percent"],
            "RTE_FUENTE": rte_fuente["amount"],
            "Porcentaje_RTE_IVA": rte_iva["percent"],
            "RTE_IVA": rte_iva["amount"],
            "Porcentaje_RTE_ICA": rte_ica["percent"],
            "RTE_ICA": rte_ica["amount"],
            "TipoComprobante": self.return_type_voucher(),
            "TipoNota": "91",
            "TipoMoneda": "COP",
            "FechaVencimiento": self.return_date_format(self.invoice_date_due),
            "TipoOperacion": type_operation,
            "CodigoConceptoNot": self.type_note_credit,
            "Notas": (self.notes_fe or "") + (self.ref or ""),
            # "TipoTransaccion": str(self.payment_method_dian_id.name).upper(),
            "TipoTransaccion": type_transaction,
            "IdProductoServicio": product_id.id,
            "CantidadProductoServicio": str(line.quantity),
            "NombreProductoServicio": str(line.product_id.name)
            .replace('"', "")
            .replace("'", ""),
            "TipoUnidadMedidaProductoServicio": product_id.unit_measure_id.code,
            "InfoAdicionalProductoServicio": line.product_id.code_cum
            if line.product_id.code_cum
            else "",
            "vendedor": str(seller),
            "ValorProductoServicio": str(line.price_unit),
            "TipoImpuesto": tax["type_tax"] if tax else "",
            "ValorImpuesto": tax["amount_tax"] if tax else "",
            "Porcentaje_Dcto": line.discount or 0,
            "Descripcion_Dcto": "SIN DESCUENTO",
            "numero_lineas": self.return_number_lines(),
            "remision": self.return_name_so(),
            #'remision': self.return_picking_name_so(),
        }

        return vals

    def return_data_line_invoice(self):
        """
        Permite retornar la data de los productos para la fe
        """
        data = []
        if self.invoice_line_ids:
            if self.move_type == "out_invoice":
                for line in self.invoice_line_ids:
                    if line.product_id:
                        data.append(self.return_structure_data_line_invoice(line))
            if self.move_type == "out_refund":
                for line in self.invoice_line_ids:
                    if line.product_id:
                        data.append(self.return_structure_data_line_notes(line))

        return data

    def return_token_operation(self):
        """
        Retorna el token de operacion
        """
        token = self.env.company.token_operation_api

        if not token:
            raise ValidationError(
                "Asegurese de haber conectado satisfactoriamente a la API. \n Para verificarlo, dirigase a la compañia en la pestaña de Facturación Electrónica."
            )
        return token

    def return_data_dian(self):
        """
        Permite armar la estructura del body para el envio de los datos hacia la API de la FE
        """
        data_line = self.return_data_line_invoice()
        data_line = [data_line]
        data_line = str(data_line)
        data_line = data_line.replace("None", "null")
        data_line = data_line.replace("'", '"')
        data_line = data_line.replace(": ", ":")
        data_line = data_line.replace(", ", ",")

        vals = {"tokenOperacion": self.return_token_operation(), "facturas": data_line}
        # vals = {"facturas": data_line}
        return vals

    def get_document_dian(self, url, is_note=False):
        """
        Permite retornar un diccionario con la respuesta de la consulta a la api DIAN
        """
        company = self.env.company
        headers = company.return_heders_api()

        body = {
            "tokenOperacion": self.return_token_operation(),
            "folio": self.return_number_invoice_dian(),
            "prefijo": self.return_prefix_invoice_dian(),
        }

        if not headers:
            raise ValidationError(
                "Se ha encontrado un problema en la configuración del Header. \n Por favor, contacte al Administrador"
            )
        if not body:
            raise ValidationError(
                "Se ha encontrado un problema en la información de la Factura. \n Por favor, contacte al Administrador"
            )
        if not url:
            raise ValidationError(
                "Debe de configurar una URL para la importación de Facturas. \n Por favor, dirigase a la Compañía en la pestaña \n - Configuración API DIAN."
            )

        if is_note:
            body["tipo_documento"] = "91"

        try:
            response = requests.post(url, data=body, headers=headers)

            if response.text:
                value_response = json.loads(response.text)
                _logger.info(self.name)
                # _logger.info(value_response)
                return value_response

        except Exception as e:
            print(e)
            raise ValidationError(
                "Ha ocurrido un problema para obtener los documentos de la Dian. Por favor, revise su red o el acceso a internet."
            )

    def get_xml_dian(self, value_response):
        """
        Permite convertir el xml de base64 a string
        """
        data_xml = None
        if value_response:
            if "attachedDocumentBase64" in value_response:
                xmlbase64 = value_response["attachedDocumentBase64"]

                base64_bytes = xmlbase64.encode("utf-8")
                data_xml = base64.decodebytes(base64_bytes)
                data_xml = data_xml.decode("utf-8", "replace")

        return data_xml

    def get_qr_dian(self, value_response):
        """
        Permite retornar el codigo qr
        """
        code_qr = None
        if value_response:
            if "QR" in value_response:
                data_qr = value_response["QR"]
                code_qr = self.generate_barcode(data_qr)

        print(code_qr)
        return code_qr

    def send_data_api_dian(self):
        """
        Permite enviar los datos de la factura a la API
        """
        company = self.env.company
        headers = company.return_heders_api()
        body = self.return_data_dian()

        url = company.url_import_invoice
        if self.move_type == "out_invoice":
            url = company.url_import_invoice
        if self.move_type == "out_refund":
            url = company.url_import_note

        url_xml = company.url_xml
        url_pdf = company.url_pdf

        if not headers:
            raise ValidationError(
                "Se ha encontrado un problema en la configuración del Header. \n Por favor, contacte al Administrador"
            )
        if not body:
            raise ValidationError(
                "Se ha encontrado un problema en la información de la Factura. \n Por favor, contacte al Administrador"
            )
        if not url:
            raise ValidationError(
                "Debe de configurar una URL para la importación de Facturas. \n Por favor, dirigase a la Compañía en la pestaña \n - Configuración API DIAN. \n - Importe Facturas."
            )

        try:
            response = requests.post(url, data=body, headers=headers)
            _logger.info("send_data_api_dian: " + str(self.name))

            if response.json():
                # print("entro")
                # value_response = json.loads(response.text)
                value_response = response.json()
                # print(type(value_response))
                if "code" in value_response:
                    if (
                        value_response["code"] != "00"
                        or value_response["code"] != "200"
                    ):
                        self.response_api = str(json.dumps((value_response), indent=4))

                self.xml_response_dian = value_response
                if "cufe" in value_response:
                    _logger.info("cufe %s" % (value_response["cufe"]))
                    self.cufe = value_response["cufe"]
                    self.generate_files_document_dian(value_response)
                    if "estado" in value_response:
                        _logger.info("estado %s" % (value_response["estado"]))
                        if value_response["estado"]:
                            self.xml_response_dian = value_response["estado"]
                            if value_response["estado"].lower().find("correctamente"):
                                self.write({"state_dian": "exitoso"})

                else:
                    self.write({"state_dian": "rechazado"})

                if "estado" in value_response:
                    if value_response["estado"]:
                        self.xml_response_dian = value_response["estado"]
                        if value_response["estado"].lower().find("correctamente"):
                            if "cufe" in value_response:
                                if value_response["cufe"]:
                                    self.cufe = value_response["cufe"]
                                    self.generate_files_document_dian(value_response)
                                    self.generate_files_document_dian(value_response)
                                    self.write({"state_dian": "exitoso"})

                else:
                    self.write({"state_dian": "rechazado"})

        except Exception as e:
            _logger.info(e)
            self.write({"state_dian": "rechazado"})
            raise ValidationError(
                "No existe comunicación con la API para el servicio de recepción de Facturas Electrónicas. Por favor, revise su red o el acceso a internet. \n Error encontrado: %s."
                % (str(e))
            )

    def send_note_credit_dian(self):
        """
        Permite enviar los datos de la nota credito a la API
        """
        company = self.env.company

        url = company.url_import_note
        url_xml = company.url_xml
        if not url:
            raise ValidationError(
                "Debe de configurar una URL para la importación de Facturas. \n Por favor, dirigase a la Compañía en la pestaña \n - Configuración API DIAN. \n - Importe Facturas."
            )

        try:

            response = self.get_document_dian(url, True)

            if response:
                self.xml_response_dian = response

                if "cude" in response:

                    self.cufe = response["cude"]

        except Exception as e:

            print(e)
            raise ValidationError(
                "No existe comunicación con la API para el servicio de recepción de Facturas Electrónicas. Por favor, revise su red o el acceso a internet."
            )

        response = self.get_document_dian(url_xml, True)
        self.get_xml_dian(response)

    def validate_dian(self):

        self.validate_fields_invoice_fe()
        self.env.company.with_context(validate_api_key=False).action_connect_api()
        # if self.move_type == 'out_invoice':
        # _logger.info('creando dian')
        self.send_data_api_dian()
        # if self.move_type == 'out_refund':
        # 	self.send_note_credit_dian()

    def action_invoice_dian_resend(self):
        """
        Permite el reenvio del correo para enviar nuevamente los documentos de la Dian
        """
        self.ensure_one()
        template = self.env.ref("connection_api_fe.email_template_invoice_dian", False)
        print(template)
        compose_form = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = dict(
            default_model="account.move",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode="comment",
            mark_invoice_as_sent=True,
        )
        return {
            "name": _("Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

    def enviar_email(self, zip_document, name_file_xml):
        """
        Permite el envio por correo electronico
        """

        rs_adjunto = self.env["ir.attachment"].sudo()
        dictAdjunto = {
            "name": name_file_xml[:-4],
            "res_id": self.id,
            "res_model": "account.move",
            # "res_model_name": "Factura",
            "res_field": None,
            "mimetype": "application/xml;charset=utf-8",
            "public": False,
            # "datas_fname": name_file_xml,
            # "res_name": name_file_xml,
            "datas": zip_document,
            "type": "binary",
        }

        nuevo_adjunto = rs_adjunto.create(dictAdjunto)

        email_template_id = self.env.ref(
            "connection_api_fe.email_template_invoice_dian", False
        )
        if email_template_id:
            email_template_id.attachment_ids = nuevo_adjunto
            email_template_id.write({"attachment_ids": nuevo_adjunto})
            # email_template_id.attachment_ids = email_template_id.attachment_ids + nuevo_adjunto
            email_template_id.send_mail(self.id, force_send=True)
            email_template_id.write({"attachment_ids": None})

        else:
            raise ValidationError(
                "No existe la plantilla de correo email_template_invoice_dian para el email"
            )
        return True

    def action_invoice_cancel(self):
        if self.state_dian == "exitoso":
            user_permission = self.env.user.has_group(
                "connection_api_fe.group_permission_cancel_invoice"
            )
            if not user_permission:
                raise ValidationError(
                    "Una Factura en estado exitoso, no puede ser cancelada"
                )
        rec = super(AccountMoveInherit, self).action_invoice_cancel()
        return rec

    @api.model
    def generate_barcode(self, data):
        """
        Permite generar el codigo qr de la factura electronica
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=2,
            border=2,
        )

        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        print(data)
        qr_image = base64.b64encode(temp.getvalue())
        # _logger.info("generate_barcode: " % (qr_image))
        return qr_image

    def create_attachment_temp(self):

        pdf = self.env.ref("account.account_invoices")._render_qweb_pdf(self.id)
        pdf = base64.b64encode(pdf[0])

        try:

            return base64.decodebytes(pdf)

        except Exception as e:
            raise ValidationError("Error al capturar el .pdf. \n Error: %s" % (str(e)))

    def search_tax_line(self, data, tax_group_id):
        """
        Funcion que permite buscar el grupo de impuesto al que pertenece el impuesto
        """
        if data:

            for x in data:
                if x["tax_group_id"] == tax_group_id:
                    return True
        return False

    def update_data_tax_line(self, data, tax_group_id, vals):
        """
        Funcion que permite actualizar la data del grupo de impuestos
        """
        data_new = []
        if data:

            for x in data:
                if x["tax_group_id"] == tax_group_id:
                    if x["taxes"]:
                        for tax in x["taxes"]:
                            data_new.append(tax)
                    data_new.append(vals)
                    x["taxes"] = data_new

    def load_line_tax_ids(self):
        """
        Funcion que permite cargar los impuestos agrupados
        """
        data = []
        for x in self.line_ids:
            if x.tax_line_id:

                vals = {
                    "account_name": x.account_id.name,
                    "account_code": x.account_id.code,
                    "tax_id": x.tax_line_id.id,
                    "tax": x.tax_line_id.name,
                    "tax_amount": x.price_total,
                    "base": x.tax_base_amount,
                    "type_tax_dian": x.tax_line_id.type_tax_dian,
                    "amount": x.tax_line_id.amount,
                }
                if self.search_tax_line(data, x.tax_group_id.id) == False:
                    value = {
                        "tax_group_id": x.tax_group_id.id,
                        "tax_group_name": x.tax_group_id.name,
                        "taxes": [vals],
                    }
                    data.append(value)
                else:
                    self.update_data_tax_line(data, x.tax_group_id.id, vals)

        return data

    def remove_files_out_refund(self):
        for record in self:
            account_ids = record.search([("move_type", "=", "out_refund")])
            if account_ids:
                for item in account_ids:
                    item.xml_file = None
                    item.pdf_file = None
                    item.zip_file = None
                    item.QR_code = None

    def return_invoice_origin_all_invoice(self):
        """
        Allow return invoice origin
        """
        for record in self:
            account_ids = record.search([("move_type", "=", "out_refund")])
            if account_ids:
                for item in account_ids:
                    ref = item.ref
                    if ref:
                        data = ref.split(" ")
                        item.invoice_origin = data[2][: len(data[2]) - 1].strip()

    @api.model
    def download_pdf(self):

        created_attachment = self.env["ir.attachment"].create(
            {
                "name": self.pdf_file_name,
                "datas": self.pdf_file,
                "db_datas": self.pdf_file,
            }
        )

        return {
            "type": "ir.actions.act_url",
            "target": "self",
            "url": "/web/content/%s?download=1" % created_attachment.id,
        }

    def count_lines(self):
        return len(self.invoice_line_ids)

    def description_currency(self):
        company_id = self.env.company
        currency = company_id.currency_id
        return "%s %s" % (currency.name, currency.currency_unit_label)

    def invoice_taxes_by_group_show(self):
        for move in self:

            # Not working on something else than invoices.
            if not move.is_invoice(include_receipts=True):
                move.amount_by_group = []
                continue

            balance_multiplicator = -1 if move.is_inbound() else 1

            tax_lines = move.line_ids.filtered("tax_line_id")
            base_lines = move.line_ids.filtered("tax_ids")

            tax_group_mapping = defaultdict(
                lambda: {
                    "base_lines": set(),
                    "base_amount": 0.0,
                    "tax_amount": 0.0,
                }
            )

            # Compute base amounts.
            for base_line in base_lines:
                base_amount = balance_multiplicator * (
                    base_line.amount_currency
                    if base_line.currency_id
                    else base_line.balance
                )

                for tax in base_line.tax_ids.flatten_taxes_hierarchy():
                    if tax.show_in_report:
                        if base_line.tax_line_id.tax_group_id == tax.tax_group_id:
                            continue

                        tax_group_vals = tax_group_mapping[tax.tax_group_id]
                        if base_line not in tax_group_vals["base_lines"]:
                            tax_group_vals["base_amount"] += base_amount
                            tax_group_vals["base_lines"].add(base_line)

            # Compute tax amounts.
            for tax_line in tax_lines:
                if tax_line.tax_line_id.show_in_report:
                    tax_amount = balance_multiplicator * (
                        tax_line.amount_currency
                        if tax_line.currency_id
                        else tax_line.balance
                    )
                    tax_group_vals = tax_group_mapping[
                        tax_line.tax_line_id.tax_group_id
                    ]
                    tax_group_vals["tax_amount"] += tax_amount

            tax_groups = sorted(tax_group_mapping.keys(), key=lambda x: x.sequence)
            amount_by_group = []
            for tax_group in tax_groups:
                tax_group_vals = tax_group_mapping[tax_group]
                amount_by_group.append(
                    (
                        tax_group.name,
                        tax_group_vals["tax_amount"],
                        tax_group_vals["base_amount"],
                        formatLang(
                            self.env,
                            tax_group_vals["tax_amount"],
                            currency_obj=move.currency_id,
                        ),
                        formatLang(
                            self.env,
                            tax_group_vals["base_amount"],
                            currency_obj=move.currency_id,
                        ),
                        len(tax_group_mapping),
                        tax_group.id,
                    )
                )
            print(amount_by_group)
            return amount_by_group

    def payment_term_inmediate(self):
        payment_term_id = self.env.ref("account.account_payment_term_immediate")
        return payment_term_id.id if payment_term_id else 0

    def update_stock_quant(self):
        _logger.info("Ejecutando query de odoo stock quant")
        quants = self.env["stock.quant"].search([])
        move_line_ids = []
        warning = ""
        for quant in quants:
            move_lines = self.env["stock.move.line"].search(
                [
                    ("product_id", "=", quant.product_id.id),
                    ("location_id", "=", quant.location_id.id),
                    ("lot_id", "=", quant.lot_id.id),
                    ("package_id", "=", quant.package_id.id),
                    ("owner_id", "=", quant.owner_id.id),
                    ("product_qty", "!=", 0),
                ]
            )
            move_line_ids += move_lines.ids
            reserved_on_move_lines = 0
            for item in move_lines:
                reserved_on_move_lines += item["product_qty"]
                # reserved_on_move_lines = sum(move_lines.mapped('product_qty'))

            move_line_str = ""
            # for item in [str(move_line_id) for move_line_id in move_lines.ids]:
            for move_line_id in move_lines.ids:
                move_line_str += str(move_line_id) + ", "
                # move_line_str = str.join(', ', [str(move_line_id) for move_line_id in move_lines.ids])

            if quant.location_id.should_bypass_reservation():
                # If a quant is in a location that should bypass the reservation, its `reserved_quantity` field
                # should be 0.
                if quant.reserved_quantity != 0:
                    quant.write({"reserved_quantity": 0})
            else:
                # If a quant is in a reservable location, its `reserved_quantity` should be exactly the sum
                # of the `product_qty` of all the partially_available / assigned move lines with the same
                # characteristics.
                if quant.reserved_quantity == 0:
                    if move_lines:
                        move_lines.with_context(bypass_reservation_update=True).write(
                            {"product_uom_qty": 0}
                        )

                elif quant.reserved_quantity < 0:
                    quant.write({"reserved_quantity": 0})
                    if move_lines:
                        move_lines.with_context(bypass_reservation_update=True).write(
                            {"product_uom_qty": 0}
                        )

                else:
                    if reserved_on_move_lines != quant.reserved_quantity:
                        move_lines.with_context(bypass_reservation_update=True).write(
                            {"product_uom_qty": 0}
                        )
                        quant.write({"reserved_quantity": 0})
                    else:
                        flag = False
                        for move_line in move_lines:
                            if move_line.product_qty < 0:
                                flag = True
                        if flag:
                            # if any(move_line.product_qty < 0 for move_line in move_lines):
                            move_lines.with_context(
                                bypass_reservation_update=True
                            ).write({"product_uom_qty": 0})
                            quant.write({"reserved_quantity": 0})

        move_lines = self.env["stock.move.line"].search(
            [
                ("product_id.type", "=", "product"),
                ("product_qty", "!=", 0),
                ("id", "not in", move_line_ids),
            ]
        )

        move_lines_to_unreserve = []

        for move_line in move_lines:
            if not move_line.location_id.should_bypass_reservation():
                move_lines_to_unreserve.append(move_line.id)

        if len(move_lines_to_unreserve) > 1:
            self.env.cr.execute(
                """ UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id in %s ;"""
                % (tuple(move_lines_to_unreserve),)
            )
        elif len(move_lines_to_unreserve) == 1:
            self.env.cr.execute(
                """ UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id = %s ;"""
                % (move_lines_to_unreserve[0])
            )

    def send_invoice_fe(self):
        """
        Permite enviar las nominas rechazadas automaticamente
        """
        invoice_ids = self.sudo().search([("state_dian", "=", "rechazado")], limit=3)
        if invoice_ids:
            for invoice in invoice_ids:
                invoice.sudo().validate_dian()

    def send_invoice_fe_cufe(self, qty: int = 5):
        """
        Permite enviar las nominas sin cufe automaticamente
        """
        invoice_ids = self.sudo().search([("cufe", "=", "")], limit=qty)
        if invoice_ids:
            for invoice in invoice_ids:
                invoice.sudo().validate_dian()

    def send_invoice_fe_state_dian(self, state_dian: str, qty: int = 5):
        """
        Permite enviar las nominas sin cufe automaticamente
        """
        invoice_ids = self.sudo().search([("state_dian", "=", state_dian)], limit=qty)
        if invoice_ids:
            for invoice in invoice_ids:
                invoice.sudo().validate_dian()

    def button_send_invoice_fe_cufe(self):
        """
        Permite enviar las nominas sin cufe automaticamente
        """
        invoice_ids = self.sudo().search(
            [("cufe", "=", ""), ("company_id", "=", 1)], order="id desc", limit=5
        )
        if invoice_ids:
            for invoice in invoice_ids:
                invoice.sudo().validate_dian()
