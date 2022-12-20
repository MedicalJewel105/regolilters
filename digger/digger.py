from os import path, chdir, walk
import json
import requests


def get_sounds_data() -> dict:
    """Fetch github repo for latest sounds data, otherwise use one installed with filter"""
    with open(path.join(DATA_PATH, 'digger', 'sounds_data.json'), 'r') as data_file:
        sounds_data = json.load(data_file)
    try:
        sounds_data = requests.get('https://raw.githubusercontent.com/MedicalJewel105/bedrock-tools-creator/main/data/sounds_data.json').json()
    except (requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
        print('[digger] [warning]: an error has ocurred while checking for the latest data')
    else:
        # save updated data
        with open(path.join(DATA_PATH, 'digger', 'sounds_data.json'), 'w') as data_file:
            json.dump(sounds_data, data_file, indent=4)
    return sounds_data

def find_tools() -> list:
    """Find 1.16.100+ items that have digger component with digger_filter key and fill in templates for such tools"""
    items_folder = path.join(BP_PATH, 'items')
    # items_folder = path.join('test', BP_PATH, 'items') # DEBUG
    if path.exists(items_folder):
        item_paths = []
        for dir, subdirs, files in walk(items_folder): # get paths of all items
            item_paths.extend([path.join(dir, file) for file in files])
    else:
        return []
    
    tools = []
    for item_path in item_paths:
        with open(item_path, 'r', encoding='UTF-8') as item_file:
            item_data = json.load(item_file)
        if tuple(map(int, item_data.get('format_version', '').split('.'))) >= tuple([1, 16, 100]): # check format version
            digger_data = item_data.get('minecraft:item', {}).get('components', {}).get('minecraft:digger', {}).get('digger_filter', False) # parse 'digger_filter'
            if digger_data:
                tool_data = {
                    'path': item_path,
                    'tool_type': digger_data.get('tool_type', ''),
                    'blacklist': digger_data.get('blacklisted', []),
                    'speed': digger_data.get('speed', 1),
                    'event': digger_data.get('event', ''),
                    'use_custom_blocks': digger_data.get('use_custom_blocks', '')
                }
                if tool_data['tool_type'] in ['axe', 'hoe', 'pickaxe', 'shovel']:
                    tools.append(tool_data)
                else: # clear filter data so MC don't raise errors
                    del item_data['minecraft:item']['components']['minecraft:digger']['digger_filter']
                    with open(item_path, 'w', encoding='UTF-8') as item_file:
                        json.dump(item_data, item_file, indent=4)
    return tools

def load_vanilla_blocks() -> dict:
    """Fetch github repo for the latest blocks.json, otherwise use one installed with filter"""
    with open(path.join(DATA_PATH, 'digger', 'blocks.json')) as data_file:
        blocks_data = json.load(data_file)
    try:
        blocks_data = requests.get('https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/blocks.json').json()
    except (requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError):
        print('[digger] [warning]: an error has ocurred while checking for the latest data')
    else:
        # save updated data
        with open(path.join(DATA_PATH, 'digger', 'blocks.json'), 'w') as data_file:
            json.dump(blocks_data, data_file)
    return blocks_data

def load_custom_blocks() -> dict:
    """Just open blocks.json in RP folder. If it exists ofc"""
    if path.exists(path.join(RP_PATH, 'blocks.json')):
        with open(path.join(RP_PATH, 'blocks.json'), 'r') as data_file:
            custom_data = json.load(data_file)
    else:
        custom_data = {}
    return custom_data

def make_tool(tool: dict, vb: dict, cb: dict, sounds_data: dict):
    """Generate and write to file destroy speed values based on provided data"""
    with open(tool['path'], 'r', encoding='UTF-8') as item_file:
        item_data = json.load(item_file)
    destroy_speeds = item_data['minecraft:item']['components']['minecraft:digger'].get('destroy_speeds', [])

    blocks_data = vb
    if tool['use_custom_blocks']: blocks_data |= cb # merge 2 dicts
    added_blocks = [b.get('block', '') for b in item_data['minecraft:item']['components']['minecraft:digger'].get('destroy_speeds', [])]
    blocks2exclude = sounds_data[f"{tool['tool_type']}_exclude"] + sounds_data['exclude'] + tool['blacklist']

    for block, block_data in blocks_data.items(): # generate from vanilla (and custom) blocks.json
        conditions_met = type(block_data) == dict and block_data.get('sound', '') in sounds_data[tool['tool_type']] and block not in blocks2exclude and block not in added_blocks
        # condition: type of block_data is dict; block's sound is in list for this tool; block is not in exclude list for this sound; block not in general exclude list (e.g. bedrock); block is not already defined by user
        if conditions_met:
            destroy_data = {
                'block': block,
                'speed': tool['speed'],
            }
            if tool['event']:
                destroy_data.update({'on_dig': {'event': tool['event']}})
            destroy_speeds.append(destroy_data)
    
    for block in sounds_data[f"{tool['tool_type']}_add"]: # add blocks from <...>_add list
        if block not in (added_blocks + blocks2exclude):
            destroy_data = {
                'block': block,
                'speed': tool['speed'],
            }
            if tool['event']:
                destroy_data.update({'on_dig': {'event': tool['event']}})
            destroy_speeds.append(destroy_data)
    
    del item_data['minecraft:item']['components']['minecraft:digger']['digger_filter']
    item_data['minecraft:item']['components']['minecraft:digger']['destroy_speeds'] = destroy_speeds

    with open(tool['path'], 'w', encoding='UTF-8') as item_file:
        json.dump(item_data, item_file, indent=4)


def main() -> None:
    """Main program"""
    # chdir(path.dirname(path.realpath(__file__))) # DEBUG
    global BP_PATH, RP_PATH, DATA_PATH
    BP_PATH = 'BP'
    RP_PATH = 'RP'
    DATA_PATH = 'data'

    sounds_data = get_sounds_data()
    tools = find_tools()
    vanilla_blocks_data = load_vanilla_blocks()
    custom_blocks_data = load_custom_blocks()

    for tool in tools:
        make_tool(tool, vanilla_blocks_data, custom_blocks_data, sounds_data)

if __name__ == '__main__':
    main()