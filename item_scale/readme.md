# item_scale

This filter generates render_offsets for 1.16.100+ items.
Offsets generated:
-   Main hand: first (not ideal) and third person view
-   Off hand: first and third person view

## Why

In 1.16.100 version and later items with icons more than 16x16 pixels started to render differently, that is why this filter was created. Please note that alculations are not idesl. 

## Using the Filter

Simply add to your filter list, like this:

```json
{
    "filter": "item_scale"
}
```

Don't forget to set `scale` value to `regolith`:

```json
"minecraft:render_offsets": {
    "scale": "regolith"
}
```

This filter won't wipe your calculations if there are ones.