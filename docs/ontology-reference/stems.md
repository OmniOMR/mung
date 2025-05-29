# Stems

Corresponding SMuFL group: [4.15. Stems](https://w3c.github.io/smufl/latest/tables/stems.html)

Class names in this group:

- [`stem`](#stem)


## `stem`

<img src="stems/stem_smufl.png" height="100" />
<img src="stems/stem_omniomr-1d507bc2-id209.png" height="100" />
<img src="stems/stem_mpp20-w01-p010-id275.png" height="100" />
<img src="stems/stem_mpp20-w01-p010-id239.png" height="100" />

The line that extends vertically up or down from a notehead. Flags and beams attach to stems.

A notehead can have two stems, if the notehead represents two simultaneous notes from two voices with the same pitch. Example:

<img src="stems/example_doubleStems_mpp20-w04-p020.png" height="150" />

🔗 **Inlinks:** From these noteheads: `noteheadHalf`, `noteheadBlack`. And from these gracenote noteheads: `noteheadHalfSmall`, `noteheadBlackSmall`.

🤖 **Validation rules:**

- `stem` must have exactly one inlink from some notehead.
