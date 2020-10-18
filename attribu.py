def check_product_import(self, convert, product, products_ext):
	id_product = self.get_map_field_by_src(self.TYPE_PRODUCT, convert['id'], convert['code'], lang = self._notice['target']['language_default'])
	if id_product:
		pro_attr = dict()
		language_code = convert.get('language_code')
		product_type = 'simple'
		if self.is_wpml() and not language_code or (self.is_polylang() and not language_code):
			language_code = self._notice['target']['language_default']
		if convert['attributes']:
			position = 0
			for option in convert['attributes']:
				if option['option_value_name'] and option['option_value_name'] != '':
					pro_attr_code = self.get_pro_attr_code_default(option)
					if (to_int(option.get('is_taxonomy')) == 1 or option['option_id'] or not self.is_woo2woo()) and option['option_type'] != 'text':
						woo_attribute_id = self.get_woo_attribute_id(pro_attr_code, option['option_name'], language_code, option)
						if not woo_attribute_id:
							values = option['option_value_name']
							if isinstance(values, list):
								attribute_product = ' | '.join(values)
							else:
								attribute_product = values
							pro_attr[pro_attr_code] = {
								'name': option['option_name'],
								'value': attribute_product,
								'position': position,
								'is_visible': 0 if ('is_visible' in option) and (not option['is_visible']) else 1,
								'is_variation': 1 if option.get('is_variation') else 0,
								'is_taxonomy': 0
							}
							position += 1
							continue

						if option['option_value_name']:
							option_value = option['option_value_name']
							descs = get_value_by_key_in_dict(option, 'option_value_description', '')
							if option['option_type'] == self.OPTION_MULTISELECT:
								option_value_list = to_str(option_value).split(';')
								desc_value_list = descs.split(';')
								for key_op, option_value_child in enumerate(option_value_list):
									new_option = copy.deepcopy(option)
									new_option['option_value_name'] = option_value_child
									new_option['position_option'] = key_op
									desc_value_child = ''
									for nk_op, desc_child in enumerate(desc_value_list):
										if to_str(nk_op) == to_str(key_op):
											desc_value_child = desc_child
									opt_value_id = self.get_woo_attribute_value(option_value_child, pro_attr_code, language_code, new_option, desc_value_child)
									if not opt_value_id:
										continue
									where_count_update = {
										'term_taxonomy_id': opt_value_id,
									}
									query_update = {
										'type': 'update',
										'query': "UPDATE _DBPRF_term_taxonomy SET `count` = `count` + 1 WHERE " + self.dict_to_where_condition(where_count_update)
									}
									self.import_data_connector(query_update, 'products')

									relationship = {
										'object_id': id_product,
										'term_taxonomy_id': opt_value_id,
										'term_order': 0
									}
									self.import_data_connector(self.create_insert_query_connector('term_relationships', relationship))
							else:
								opt_value_id = self.get_woo_attribute_value(option_value, pro_attr_code, language_code, option, descs)
								if not opt_value_id:
									continue
								where_count_update = {
									'term_taxonomy_id': opt_value_id,
								}
								query_update = {
									'type': 'update',
									'query': "UPDATE _DBPRF_term_taxonomy SET `count` = `count` + 1 WHERE " + self.dict_to_where_condition(where_count_update)
								}
								self.import_data_connector(query_update, 'products')

								relationship = {
									'object_id': id_product,
									'term_taxonomy_id': opt_value_id,
									'term_order': 0
								}
								self.import_data_connector(self.create_insert_query_connector('term_relationships', relationship))

						pro_attr["pa_" + pro_attr_code] = {
							'name': "pa_" + urllib.parse.unquote_plus(pro_attr_code),
							'value': '',
							'position': position,
							'is_visible': 0 if ('is_visible' in option) and (not option['is_visible']) else 1,
							'is_variation': 1 if option.get('is_variation') else 0,
							'is_taxonomy': 1
						}
						position += 1
					else:
						values = option['option_value_name']
						if option['option_type'] == self.OPTION_MULTISELECT:
							list_value = to_str(values).split(';')
							values = ' | '.join(list_value)
						attribute_product = values
						pro_attr[pro_attr_code] = {
							'name': option['option_name'],
							'value': attribute_product,
							'position': position,
							'is_visible': 0 if ('is_visible' in option) and (not option['is_visible']) else 1,
							'is_variation': 1 if option.get('is_variation') else 0,
							'is_taxonomy': 0
						}
						position += 1

			if pro_attr:
				update_attr_data = {
					'meta_value': php_serialize(pro_attr)
				}
				where_attr_update = {
					'post_id': id_product,
					'meta_key': '_product_attributes'
				}
				self.import_data_connector(self.create_update_query_connector("postmeta", update_attr_data, where_attr_update))
	return self.get_map_field_by_src(self.TYPE_PRODUCT, convert['id'], convert['code'], lang = self._notice['target']['language_default'])
