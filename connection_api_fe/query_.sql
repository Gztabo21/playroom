INSERT INTO dian_fiscal_responsability_res_partner_rel (SELECT id, 24 FROM res_partner WHERE id not in (SELECT res_partner_id FROM dian_fiscal_responsability_res_partner_rel));

UPDATE product_product
SET unit_measure_id = (SELECT id FROM product_unit_measures_fe WHERE code = '94');


UPDATE dian_fiscal_responsability
SET active = True
WHERE code in ('O-47', 'O-48', 'O-49', 'R-99-PN', 'O-13', 'O-15', 'O-23');

UPDATE account_move
SET notes_fe = '', cufe = '', xml_response_dian = '', xml_response = '', guide_number = '', pdf_file_save = '', zip_file_name = '', xml_file_name = '', state_dian = 'por_notificar', xml_file = null, zip_file = null, pdf_file = null
WHERE move_type = 'out_refund';