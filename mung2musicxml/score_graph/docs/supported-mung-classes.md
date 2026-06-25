# Supported MuNG Classes

> **Last revision: March 7nd 2026**

> **Based on Annotation instructions from: [Feb 6th 2026](https://github.com/OmniOMR/mung/blob/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/annotation-instructions.md)**

This document goes over classes from MuNG that are are implemented in ScoreGraph, the list is based on [Annotation Instructions](https://github.com/OmniOMR/mung/blob/main/docs/annotation-instructions/annotation-instructions.md). For potential limitations of **implemented** classes see [Exporter Limitations](./musicxml-exporter-limitations.md) and [MusicXML Limitations](./musicxml-limitations.md).

There are four levels of implementation:

- ✅ Implemented explicitly, an object in ScoreGraph.
- ☑️ Implemented as part of another object.
- 🚧 Partially implemented.
- ❌ Not implemented.

## Staves

- ☑️ `staffLine` - used to determine pitch.
- ☑️ `staffSpace` - used to determine pitch.
- ✅ `staff`

## Noteheads

- ✅ `noteheadWhole`
- ✅ `noteheadHalf`
- ✅ `noteheadBlack`

<p>
  <img src="./images/noteheads-overview.png" height="100">
</p>

## Grace Noteheads

Grace noteheads are partially implemented but, in this version, they cannot form chords. Slurs and ties that include grace notes are not supported.

- 🚧 `noteheadBlackSmall`
- 🚧 `noteheadWholeSmall`
- 🚧 `noteheadHalfSmall`
- ❌ `graceNoteSlashStemUp`
- ❌ `graceNoteSlashStemDown`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/grace-element.png" height="100">
</p>

## Noteheads attachments

- ✅ `augmentationDot`

<p style="background-color: white; display: inline-block;">
  <img src="https://usermanuals.musicxml.com/MusicXML/Content/MusicXML_files/780942df-789b-447f-b5bc-59201478fb7e.png" height="100">
</p>

- ☑️ `stem` - property of a notehead.

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/stem-value-up.png" height="100">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/stem-value-down.png" height="100">
</p>

- ☑️ `flag(number)th(Up/Down)` - used to determine duration.

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/flags-0.png" height="100">
</p>

- ✅ `beam`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/elements/beam.png" height="100">
</p>

- ☑️ `legerLine` - used to determine pitch.

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/legerLine-0.png" height="100">
</p>

- ✅ `slur`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/slur-element.png" height="100">
</p>

- ✅ `tie`

<p>
  <img src="https://www.w3.org/2021/06/musicxml40/static/elements/tied.png" height="100">
</p>

## Rests

- ✅ `rest32nd`
- ✅ `rest16th`
- ✅ `rest8th`
- ✅ `restQuarter`
- ✅ `restHalf`
- ✅ `restWhole`
- ✅ `restLonga`
- ✅ `restDoubleWhole`

<p>
  <img src="./images/rests-overview.png" height="100">
</p>

- 🚧 `restHBar`
- ❌ `restText`


## Accidentals

Accidentals are implemented via `Pitch` and its property `Alter` and also as a separate object `Accidental`.

- ✅ `accidentalFlat`
- ✅ `accidentalNatural`
- ✅ `accidentalSharp`
- ✅ `accidentalDoubleSharp`
- ✅ `accidentalDoubleFlat`

<p>
  <img src="./images/accidentals-overview.png" height="100">
</p>

## Clefs

ScoreGraph makes no difference between clefs at the starf of a system (`{g,f,c}Clef`) and other clefs (`{g,f,c}ClefChange`).

- ✅ `gClef`
- ✅ `gClefChange`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/clef-G.png" height="50">
</p>

- ✅ `fClef`
- ✅ `fClefChange`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/clef-F.png" height="50">
</p>

- ✅ `cClef`
- ✅ `cClefChange`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/clef-C.png" height="50">
</p>

## Key signature

- ✅ `keySignature`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/key-element-traditional.png" height="100">
</p>

## Time Signatures

- ✅ `timeSignature`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/elements/time.png" height="100">
</p>

- ✅ `timeSig[0..9]`
- ✅ `timeSigCommon`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/time-symbol-common.png" height="100">
</p>

- ✅ `mensuralProlationCombiningDot`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/mensuralProlation5-0.png" height="100">
</p>

- ✅ `timeSigCutCommon`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/time-symbol-cut.png" height="100">
</p>

- ✅ `timeSigSlash`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/time-separator-diagonal.png" height="100">
</p>

- ✅ `timeSigFractionalSlash`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/timeSigFractionalSlash-0.png" height="100">
</p>

- ❌ `timeSigPlus`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/timeSigPlus-0.png" height="100">
</p>

- ❌ `timeSigEquals`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/timeSigEquals-0.png" height="100">
</p>

## Lyrics

- ✅ `lyricsText`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/elements/lyric.png" height="100">
</p>

- ✅ `verseNumber`

<p>
  <img src="./images/verse-number.png" height="100">
</p>

- ✅ `lyricsUnisono` - for more info see [MusicXML Limitations](./musicxml-limitations.md#lyrics-unisono).

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/lyricsUnisono-1.png" height="100">
</p>


## Tempo

- ✅ `tempoText`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/tempoText-3.png" height="100">
</p>

- ✅ `tempoRitardando`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/tempoRitardando-2.png" height="100">
</p>

- ❌ `tempoRitardandoSpanner`
- ✅ `tempoAccelerando`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/tempoAccelerando-1.png" height="100">
</p>

- ❌ `tempoAccelerandoSpanner`
- ✅ `tempoATempo`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/tempoATempo-1.png" height="100">
</p>

## Text

- ✅ `interpretationText`
- ❌ `metadataText`
- ❌ `measureNumber`

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/elements/measure-numbering.png" height="100">
</p>

- ❌ `pageNumber`
- ❌ `otherText`

## Barlines

- ✅ `barlineSingle`.

<p style="background-color: white; display: inline-block;">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/bar-style-regular.png" height="100">
</p>

- ✅ `barlineHeavy`.

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/datatypes/bar-style-heavy.png" height="100">
</p>

- ✅ `barlineFinal` - resolved into barline `heavy-heavy`, for more info see [MusicXML Limitations](./musicxml-limitations.md#barline-final)

<p> 
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/barlineFinal-0.png" height="100">
</p>

- ☑️ `barlineWing` - property of a repeat barline.

<p> 
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/barlineWing-0.png" height="100">
</p>

- ☑️ `measureSeparator` - separator contains individual barlines that are resolved into `BarStyle` (`regular`, `light-heavy`, ...).

## Staff Brackets and Dividers

`brace` and `bracket` are properties of instrument groupings. `staffGrouping` is used to determine systems, instrument groups and grand staffs.

- ✅ `brace`

<p> 
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/brace-0.png" height="100">
</p>

- ✅ `bracket`

<p> 
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/bracket-0.png" height="100">
</p>

- ☑️ `staffGrouping`
- ❌ `systemDivider`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/system-dividers-element.png" height="200">
</p>

## Articulation

- ✅ `articAccentAbove`
- ✅ `articAccentBelow`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/accent-element.png" height="100">
</p>

- ✅ `articStaccatoAbove`
- ✅ `articStaccatoBelow`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/articulations-element.png" height="100">
</p>

- ✅ `articTenutoAbove`
- ✅ `articTenutoBelow`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/tenuto-element.png" height="100">
</p>

- ✅ `articStaccatissimoAbove`
- ✅ `articStaccatissimoBelow`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/staccatissimo-element.png" height="100">
</p>

- ✅ `articMarcatoAbove`
- ✅ `articMarcatoBelow`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/strong-accent-element.png" height="100">
</p>

## Dynamics

- ✅ `dynamicsText`
- ✅ `dynamicPiano`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/p-element.png" height="100">
</p>

- ✅ `dynamicMezzo`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/mf-element.png" height="100">
</p>

- ✅ `dynamicForte`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/f-element.png" height="100">
</p>

- ✅ `dynamicRinforzando`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/rf-element.png" height="100">
</p>

- ✅ `dynamicSforzando`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/sf-element.png" height="100">
</p>

- ✅ `dynamicZ`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/fz-element.png" height="100">
</p>

- ✅ `dynamicNiente`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/n-element.png" height="100">
</p>

- ✅ `dynamicDiminuendo`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/dynamicDiminuendo-0.png" height="100">
</p>

- ✅ `dynamicCrescendo`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/dynamicCrescendo-0.png" height="100">
</p>

- ✅ `dynamicCrescendoHairpin`
- ✅ `dynamicDiminuendoHairpin`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/wedge-element.png" height="100">
</p>

- ❌ `dynamicNienteForHairpin`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/1c569e916c21ad685a0a2783b59c61efc129ca5d/docs/annotation-instructions/img/dynamicNienteForHairpin-0.png" height=100>
</p>

## Repeats

Repeats are supported, but, some the possible bar styles are not supported by MSS4. We default to using those compatible with MSS4. For more info see [MuseScore Limitations](./musescore-limitations.md#unable-to-display-other-than-light-heavy-repeats---potentially-). MSS4 cannot import repeats that are located in the middle of a measure, see [MuseScore Limitation](./musescore-limitations.md#repeat-in-the-middle-of-a-measure-).

- ✅ `repeatLeft`
- ✅ `repeatRight`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/1c569e916c21ad685a0a2783b59c61efc129ca5d/docs/annotation-instructions/img/repeats-0.png" height="100">
</p>

- ☑️ `repeatDot` - there is not way in MusicXML to specify number of dots for a repeat, it is part of the repeat objects.

<p>
  <img src="https://github.com/OmniOMR/mung/raw/1c569e916c21ad685a0a2783b59c61efc129ca5d/docs/annotation-instructions/img/repeatDot-0.png" height="100">
</p>

- ❌ `volta`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/1c569e916c21ad685a0a2783b59c61efc129ca5d/docs/annotation-instructions/img/volta-0.png" height="100">
</p>

- ❌ `voltaText`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/voltaText-0.png" height="100">
</p>

- ❌ `segno`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/segno-element.png" height="100">
</p>

- ❌ `coda`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/coda-element.png" height="100">
</p>

- ❌ `segnoSerpent`

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/segnoSerpent-0.png" height="100">
</p>

- ❌ `repeatText`
- 🚧 `repeat1Bar` - for more info see [Exporter Limitations](./musicxml-exporter-limitations.md).

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/elements/measure-repeat.png" height="100">
</p>

## Unisono

- ❌ `unisonoText`
- ❌ `unisonoContinuation`

## Tuplets


- ✅ `tuplet` - for more info see [Exporter Limitations](./musicxml-exporter-limitations.md).

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/tuplet-element-regular.png" height="100">
</p>

- ☑️ `tuplet[0..9]` - used to determine tuplet effect on linked durables.
- ☑️ `tupletBracket` - property of tuplet.
- ❌ `tupletColon`

## Tremolo

- ✅ `tremolo[1..5]`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/tremolo-element-single.png" height="100">
</p>

- ✅ `tremoloBeam`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/tremolo-element-double.png" height="100">
</p>

## Fermata

- ✅ `fermataAbove`
- ✅ `fermataBelow`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/elements/fermata.png" height="100">
</p>

## Ornaments

- ❌ `ornamentTrill`
- ❌ `wiggleTrill`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/trill-mark-element.png" height="100">
</p>

- ❌ `ornamentTurn`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/turn-element.png" height="100">
</p>

- ❌ `ornamentTurnInverted`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/inverted-turn-element.png" height="100">
</p>

- ❌ `ornamentShortTrill`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/inverted-mordent-element.png" height="100">
</p>

- ❌ `custos`

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/schleifer-element.png" height="100">
</p>

## Unclassified

- ❌ `unclassified`
- ❌ `UFO`
