# ScoreGraph

ScoreGraph is a graph representation of music notation heavily inspired by the [MusicXML 4.0 standard](https://www.w3.org/2021/06/musicxml40/). ScoreGraph is a cluster of dataclass instances that are interlinked. The architecture is derived from [Smashcima](https://github.com/OMR-Research/Smashcima).

Abstract classes for loaders and exporters are provided. Once the graph is loaded it can be exported to any format for which the exported is implemented.

## Limitations of MuNG to MusicXML conversion

These documents cover potential issues that the user might run into while using our convertor and MuseScore:

- [MuseScore Limitations](docs/musescore-limitations.md)
- [MusicXML Exporter Limitations](docs/musicxml-exporter-limitations.md)
- [MusicXML Limitations](docs/musicxml-limitations.md)

## Design principles

- Object names and their design should be defined with respect to their MusicXML 4.0 equivalent.
- ScoreGraph construction and its export should be two separate procedures.
- During ScoreGraph construction, decisions should not be made based on the output format.
- Implementation of MusicXML exporter should follow conventions set by MuseScore Studio 4 (MSS4) as our main goal is to make the documents readable and editable in this software.
- Any discrepancy found withing the graph while loading and exporting should be logged for the user to see.

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