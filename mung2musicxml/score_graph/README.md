# ScoreGraph

ScoreGraph is a graph representation of music notation heavily inspired by the [MusicXML 4.0 standard](https://www.w3.org/2021/06/musicxml40/).

The class structure is designed in such way, that it *should not* be hard to implement loaders or exporters from or to any format.

## Design principles

- Object names and their design should be defined with respect to their MusicXML 4.0 equivalent.
- ScoreGraph construction and its export (to MusicXML) should be two separate procedures.
- During ScoreGraph construction, decisions should not be made based on the output format (MusicXML). Some examples:
    - The "Slurs are represented with two `<slur>` elements: one with a start type, and one with a stop type. ", but sometimes, in MuNG, a slur is linked to one durable only.
        - The ScoreGraph should contain that slur.
        - The export script has to solve it on its own.
    - `Repeat1Bar` symbol cannot be linked (in MusicXML) to accents, slurs, etc. because the repeat is a property of its measure, it is not a symbol on staff.
        - Again, the ScoreGraph loader should treat it as a valid durable, symbol on a staff.
        - The export script has to solve it on its own.
- The output script should try to follow conventions set by MuseScore Studio 4 (referred to sometimes as only MuseScore 4) as our main goal is to make the documents readable and editable in this software.
- Any discrepancy found, should be logged for the user to see when any work is done on/with the graph.

<!-- 
# Convertor documentation

- Event
    - all music that starts at the same time


- 3 main types of durables that play in the same voice and have the same onset (event but we restrict it to the same voice)
    - chord (made out of notes)
    - rest
    - repeat one bar and other similar symbols

Let's call these "Subevent" as they are not a full event

So the hierarchy is:

```
Event
|-- Subevent
|   |-- Chord
|   |   |-- Note
|   |-- Rest
|   |-- Other (Repeat One Bar)
```

Subevents are sequentially written into the final MusicXML - the output iterates through instruments, measures, voices, subevents. -->