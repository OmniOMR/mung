# mung2musicxml

**mung2musicxml** is a converter from Music Notation Graph (MuNG) format into MusicXML, a widely adopted standard for digital music notation. It forms an essential bridge between MuNG - a possible output representation for neural networks - and the broader OMR ecosystem.

![](./score_graph/docs/images/converter-showcase.png)

## Usage

Input to the converter should be a valid MuNG file, to create one, [MuNG Studio](https://github.com/OmniOMR/mung-studio) can be used.

After cloning, setup venv and install libraries listed in `requirements.txt`.

```
python -m mung2musicxml input/file [-o output/file] [--log-level {NONE,DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-v] [-q] [--skip-broken-measure]

input                  Input MuNG file to process.
-h, --help             Show this help message and exit.
--log-level            {NONE,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                       Set the logging verbosity level (default: INFO)
-v, --verbose          Shorthand for --log-level DEBUG (default: False)
-q, --quiet            Shorthand for --log-level WARNING (default: False)
--output, -o           Output file or dir (default: None)
--skip-broken-measure  Skips broken measures in export (default: False)
```

### Example usage

```
python -m mung2musicxml input/file.xml --skip-broken-measure -o output.musicxml --log-level WARNING
```

### Demo

See [demo README](./demo/README.md).

```
python -m mung2musicxml mung2musicxml/demo/assets/13abc7f9-5e3f-4e85-b753-0dab090728fe_9d4412a1-0cf3-4475-a022-9f37984272fb/mung.xml -o output.musicxml
```

### Run in batch mode

Create a `.txt` file listing paths to files that should be converted. Paths should be relative with respect to the directory in which the batch file is (individual MuNG files are loaded as `path/to/batch-file/line-in-batch-file`).

In batch mode, the output argument is used as a directory to which the converted files are saved.

```
# batch.txt
path/to/file1
path/to/file2
path/to/file3
```

```
# will run in batch mode
python -m mung2musicxml batch.txt

# demo
python -m mung2musicxml mung2musicxml/demo/assets/batch.txt -o converted-demo
```

## Pipeline overview

Turning Music Notation Graph (MuNG) into Musicxml, a widely adopted standard for digital music notation, requires multiple steps:

- **Preprocessing**:
    - Resolving multistem noteheads, [documentation](./preprocessing/multistem/README.md).
    - Inferring onsets and pitches.
    - Inferring voices, [documentation](./preprocessing/voices/README.md).

- **Conversion**:
    - Loading MuNG into ScoreGraph, [ScoreGraph documentation](./score_graph/README.md).
    - Exporting ScoreGraph to MusicXML.

## Limitations

We classify potential limitations into three types: those related to the exporter itself, limitations of MusicXML, and in the process we also found limitations of MuseScore for inspecting the conversion results and using it for MusicXML canonization:

- [MuseScore Limitations](./score_graph/docs/musescore-limitations.md)
- [MusicXML Exporter Limitations](./score_graph/docs/musicxml-exporter-limitations.md)
- [MusicXML Limitations](./score_graph/docs/musicxml-limitations.md)
