import json

STANDARD_INDENT = '    '
BASE_INDENT_SAVE_ZMOD_DATA = 1

def add_save_zmod_data(file_data, categories, settings):
    indent_level = BASE_INDENT_SAVE_ZMOD_DATA
    
    file_data.append((indent_level * STANDARD_INDENT) + '# ** BEGIN SAVE_ZMOD_DATA TEMPLATE SETTINGS ** #')
    file_data.append(indent_level * STANDARD_INDENT)
    for category, cat_data in categories.items():
        for setting, set_data in settings.items():
            if set_data.get('category', '') != category or set_data.get('type', '') == 'special':
                continue
            
            if set_data.get('require_ad5x', 0) != 0:
                if set_data.get('require_ad5x', 0) > 0:
                    file_data.append((indent_level * STANDARD_INDENT) + "{% if client.ad5x %}")
                else:
                    file_data.append((indent_level * STANDARD_INDENT) + "{% if not client.ad5x %}")
                indent_level += 1
                
            file_data.append((indent_level * STANDARD_INDENT) + f"{{% if params.{setting.upper()} %}}")
            indent_level += 1
            
            if set_data.get('type', '') == 'string':
                file_data.append((indent_level * STANDARD_INDENT) + f"{{ set z{setting} = params.{setting.upper()}|default(\"{set_data['default']}\")|{set_data['type']} %}}")
                file_data.append((indent_level * STANDARD_INDENT) + f"SAVE_VARIABLE VARIABLE={setting.lower()} VALUE=\"{{z{setting.lower()}}}\"")
            else:
                file_data.append((indent_level * STANDARD_INDENT) + f"{{ set z{setting} = params.{setting.upper()}|default({set_data['default']})|{set_data['type']} %}}")
                file_data.append((indent_level * STANDARD_INDENT) + f"SAVE_VARIABLE VARIABLE={setting.lower()} VALUE={{z{setting.lower()}}}")
            
            indent_level -= 1
            file_data.append((indent_level * STANDARD_INDENT) + "{% endif %}")
                                 
            if set_data.get('require_ad5x', 0) != 0:
                indent_level -= 1
                file_data.append((indent_level * STANDARD_INDENT) + "{% endif %}")
                                
            file_data.append(indent_level * STANDARD_INDENT)
            
    file_data.append((indent_level * STANDARD_INDENT) + '# ** END SAVE_ZMOD_DATA TEMPLATE SETTINGS ** #')
            
"""
    {% if params.STOP_MOTOR %}
        {% set zstop_motor = params.STOP_MOTOR|default(1)|int %}
        SAVE_VARIABLE VARIABLE=stop_motor VALUE={zstop_motor|int}
    {% endif %}
"""

def main():
    with open('zmod_settings.json', 'r', encoding='utf-8') as f:
        settings_json_data = json.load(f)
        
    categories = settings_json_data['Categories']
    settings = settings_json_data['Settings']
    
    file_data = []
    
    with open('base.cfg', 'r', encoding='utf-8') as f:
        skip_mode = False
        for line in f:
            if line.strip().startswith('# ** BEGIN'):
                skip_mode = True
                if line.strip() == '# ** BEGIN SAVE_ZMOD_DATA TEMPLATE SETTINGS ** #':
                    add_save_zmod_data(file_data, categories, settings)
                #if line.strip() == '# ** BEGIN GET_ZMOD_DATA TEMPLATE SETTINGS ** #':
                #    add_get_zmod_data(file_data, categories, settings)
                #if line.strip() == '# ** BEGIN _GLOBAL TEMPLATE SETTINGS ** #':
                #    add_global(file_data, categories, settings)
            if not skip_mode:
                file_data += [line]
            if line.strip().startswith('# ** END'):
                skip_mode = False
                
    with open('base-out.cfg', 'w', encoding='utf-8') as f:
        for line in file_data:
            f.write(line)
            if not line.endswith('\n'):
                f.write('\n')

if __name__ == "__main__":
    main()