## MusicXML specifics

- Cannot link slurs (and other spanners) to repeats - slur is child of notations (child of note). Repeat one bar is outputted as a measure repeats (child of measure style child of attributes child of measure)

    - [Slurs](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/slur/)
    - [Measure repeat](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/measure-repeat/)

![](repeat1bar-and-slur.png)

- Unable to create single subevent slurs (going only from one durable):
    - When the repeat symbol should be the stop of that durable, the slur can be outputted as a let-ring tie (tie starting from a durable )

<p>
<img src="slur-save-example.png" height="100">
<img src="slur-save-musescore-example.png" height="100" >
</p>

<p>
<img src="slur-to-repeat.png" height="100">
<img src="slur-to-repeat-musescore.png" height="100" >
</p>

- Unfortunately we were not able to find any workaround for situations like this:

<p>
<img src="slur-unsavable-example.png" height="100">
<img src="slur-unsavable-musescore-example.png" height="100" >
</p>


### Complex symbols

When the double stemmed notehead has an accidental attached to it, should we link it to both original and ghost? How do MusicXML and MuseScore handle it?

There is a way in MuseScore `3.6.2` to show two accidentals before a double stemmed note, this is most probably a bug, as reloading the file results in only one of the accidentals being displayed. Note that this is not flat-flat (double flat).

![](accidentals-ms-bug.png)

MuseScore saves the second accidental with tags `cautionary="yes" parenthesis="yes"` which hides it. After testing, it turns out that adding the accidental element without any tags, as if these were two totally unrelated notes, suffices.