# Resolving multistem (double stemmed noteheads)

The current strategy is to split the notehead into two and reassign other notation to them based on its relative position. The notehead symbol, that is present in the graph before this preprocessing step, will be called *original*, and the other, copied, a *ghost*.

## Examples

![](docs/image-1.png)

![](docs/049fd427-418f-4ef8-8944-4108b977d7be_8e821944-96e2-4a35-954f-a824ad09188c_4.png)

![](docs/334c2e20-cadf-4b30-8c21-8426a686b950_2405cebe-37f0-4a60-932c-f443027246e6_1.png)

![](docs/3bb9e322-bc61-4307-856b-6f8fb1a640df_42e422a0-fb55-423c-9ab4-91de73fa3f20_1.png)

## Complex cases

### Notes with different durations

A situation, in which the original and ghost end up having different durations is not uncommon.
In this example, there are actually three voices on the left, two 8th notes and one quarter note. There should be an edge between the double stemmed notehead and the quarter note on the right - if they were written as three separate notes.

![](docs/049fd427-418f-4ef8-8944-4108b977d7be_8e821944-96e2-4a35-954f-a824ad09188c_2.png)

This is an incorrect use of notation, the author took a shortcut and assumes that a voice suddenly appears and disappears with a single note.

![](docs/049fd427-418f-4ef8-8944-4108b977d7be_8e821944-96e2-4a35-954f-a824ad09188c_3.png)

The best (an easiest to implement) solution would be to not have any outgoing edges from the note with longer duration. Our duration inference engine can handle these cases.

### Different types of noteheads reduced to one

This is another example of what could be considered a bad practice. Once again, the author took a shortcut and created something we cannot be certain is intentional or merely an error that originated earlier in the pipeline.

![](docs/13abc7f9-5e3f-4e85-b753-0dab090728fe_dc73c953-7614-4b97-b968-927f4390e3e4_1.png)

There is no way of resolving this correctly into the two voices as such:

![](docs/musescore-example.png)

Again, in this case, the algorithm would leave the longer notehead without any precedence outlinks.

## Shared and divided symbols

There are multiple symbols that need to be reassigned to the correct notehead as they do not apply to both noteheads. By default, these are:

- flags,
- beams,
- single tremolos and tremolo beams.

Other symbols are shared between these two, by default:

- staffline, staffspace, staff,
- leger lines,
- accidentals.
