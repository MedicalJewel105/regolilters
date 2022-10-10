from PIL import Image
import json
import os
from copy import deepcopy


def find_items(path: str):
    found_items = []
    if os.path.exists(path):
        for path, subdirs, files in os.walk(path):
            for name in files:
                found_items.append(os.path.join(path, name))
    return found_items

def calculate_scale_fp(texture_size: int):
    default_scale = 0.039 # nearly correct
    calculated_scale = round(default_scale*16/texture_size, 8)
    return [calculated_scale]*3

def calculate_scale_fp_offhand(texture_size: int):
    default_scale = 0.065
    calculated_scale = round(default_scale*16/texture_size, 8)
    return [calculated_scale]*3

def calculate_scale_tp(texture_size: int):
    default_scale = 0.0965
    calculated_scale = round(default_scale*16/texture_size, 8)
    return [calculated_scale]*3

def calculate_scale_tp_offhand(texture_size: int):
    default_scale = 0.0965
    calculated_scale = round(default_scale*16/texture_size, 8)
    return [calculated_scale]*3

def get_texture_data(rp_path: str, items_data: dict):
    try:
        with open(os.path.join(rp_path, 'textures', 'item_texture.json'), 'r') as item_texture_file:
            item_texture_data = json.load(item_texture_file)
        for item in items_data:
            if texture_size := item_texture_data.get('texture_data', {}).get(items_data[item], {}).get('textures', False):
                texture_path = rp_path
                for path_part in texture_size.split('/'):
                    texture_path = os.path.join(texture_path, path_part)
                try:
                    (texture_width, texture_height) = Image.open(texture_path+'.png').size
                    if texture_width != texture_height or texture_width == 16:
                        texture_size = False # 16 # DEBUG
                    else:
                        texture_size = texture_width
                except:
                    texture_size = False
            items_data[item] = texture_size
    except:
        for item in items_data:
            items_data[item] = False
    return items_data

def main():
    BP_PATH = 'BP'
    RP_PATH = 'RP'
    item_paths = []
    items_data = {}
    item_paths += find_items(os.path.join(BP_PATH, 'items'))
    if os.path.exists(sp_path:=os.path.join(BP_PATH, 'subpacks')):
        for subpack in os.listdir(sp_path):
            item_paths += find_items(os.path.join(sp_path, subpack, 'items'))
    for item_path in item_paths:
        with open(item_path, 'r') as item:
            item_data = json.load(item)
        if tuple(map(int, item_data['format_version'].split('.'))) >= tuple([1, 16, 100]) and item_data.get('minecraft:item', {}).get('components', {}).get('minecraft:render_offsets', {}).get('scale', {}) == 'regolith':
            if item_icon := item_data['minecraft:item']['components'].get('minecraft:icon', {}).get('texture', False):
                items_data[item_path] = item_icon
    for item_path, texture_size in get_texture_data(RP_PATH, items_data).items():
        with open(item_path, 'r') as item_file:
            item_data = json.load(item_file)
        if item_data['minecraft:item']['components']['minecraft:render_offsets'].get('scale', '') == 'regolith':
            item_data['minecraft:item']['components']['minecraft:render_offsets'].pop('scale')
            if texture_size:
                modified_item_data = deepcopy(item_data)
                modified_item_data['minecraft:item']['components']['minecraft:render_offsets'] = {
                    "main_hand": {
                        "first_person": {
                            "scale": calculate_scale_fp(texture_size)
                        },
                        "third_person": {
                            "scale": calculate_scale_tp(texture_size)
                        }
                    },
                    "off_hand": {
                        "first_person": {
                            "scale": calculate_scale_fp_offhand(texture_size)
                        },
                        "third_person": {
                            "scale": calculate_scale_tp_offhand(texture_size)
                        }
                    }
                }
                for hand in ['main_hand', 'off_hand']:
                    for view in ['first_person', 'third_person']:
                        for key, value in item_data['minecraft:item']['components']['minecraft:render_offsets'].get(hand, {}).get(view, {}).items():
                            modified_item_data['minecraft:item']['components']['minecraft:render_offsets'][hand][view][key] = value
                item_data = item_data | modified_item_data
        with open(item_path, 'w') as item_file:
            json.dump(item_data, item_file, indent=4)

if __name__ == '__main__':
    main()