## MusicXML 4.0 Limitations

This documents limitations of the MusicXML 4.0 standard:

### Slurs cannot be linked to repeat symbols

Cannot link slurs (and other similar objects) to repeats. Slur are a notation attribute of a note. Repeat one bar is an attribute of the whole measure. Documentation: [Slurs](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/slur/), [Measure repeat](https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/measure-repeat/).

<p>
<img src="images/slur-to-repeat.png" height="100">
<img src="images/repeat1bar-and-slur.png" height="100">
</p>

### Slurs and ties and missing start/end durables

Slurs must have start and end, so hanging slurs at the end of a staff or at the start are not possible. Same goes for ties, with one exception: `let-ring` type allows for ties that start at a durable and end right behind it without the need for an end durable.

In the example below, the second tie uses `let-ring`:

<p style="background-color: white; display: inline-block; ">
  <img src="https://www.w3.org/2021/06/musicxml40/static/examples/tied-element.png" height="200">
</p>


### Lyrics Unisono

Lyric unisono is not part of SMuFL, character does not exist for it so we are not able to display it properly. 

We use `//` instead inside a standard MusicXML lyric object.

<p>
  <img src="images/lyrics-unisono-document.png" height="200">
</p>

<p>
  <img src="images/lyrics-unisono-solution.png" height="200">
</p>

### Barline Final

MusicXML contains no such object. We resolve it into barline with style `heavy-heavy`.

<p>
  <img src="https://github.com/OmniOMR/mung/raw/7bddc87d61e19b62ac46834a66c88239dbfebdc5/docs/annotation-instructions/img/barlineFinal-0.png" height="200">
</p>
