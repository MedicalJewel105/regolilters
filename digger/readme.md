# digger

Simple filter that adds vanilla (and custom) blocks to your tools in 1.16.100+ version.

## Features

-   Select tool type: hoe, shovel, sword, axe or pickaxe
-   Set destroy speed
-   Set on_dig event name
-   Blacklist for blocks
-   Support for custom blocks (they need to have sounds defined in blocks.json)
-   No custom data wipe

## Why

In 1.16.100 version `minecraft:digger` component appeared so now add-on developers are able to create custom tools. The developers wanted the best, but it turned out the same as always, you can't just use tags like `stone` or `metal` to cover all that blocks as not all blocks have these tags. That is why you need to add them manually. You can read about this component [here](https://wiki.bedrock.dev/items/items-16.html#minecraft-digger).  

## Using the Filter

Installation: `regolith install digger`

Simply add it to your filter list, like this:

```json
{
    "filter": "digger"
}
```

Add this to your item:

```json
{
    "minecraft:digger": {
        "digger_filter": {
            "tool_type": "axe", // hoe, shovel, and pickaxe also
            "blacklisted": [
                "block1",
                "block2",
                "block3"
            ],
            "speed": 5,
            "event": "event_name", // leave empty space if you don't need an event to be called
            "use_custom_blocks": true // will take your blocks from blocks.json in RP folder
        },

        "destroy_speeds": [
            {
                // some custom data
            }
        ]
    }
}
```

Note that you might need to use [json cleaner](https://github.com/Bedrock-OSS/regolith-filters/tree/master/json_cleaner) filter.

## How it works

Script sorts blocks to categories by their names (there are some default blacklist values which you can overwrite) and uses provided data to generate values when going through vanilla/custom blocks.json file.
Sounds are already sorted by developer, you can view them [here](https://github.com/MedicalJewel105/bedrock-tools-creator/blob/main/data/sounds_data.json).
Please, make sure to include namespace into blocks.json!