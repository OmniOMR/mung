
## Tips
- When creating a polygon, you can go **one point back** by **right-clicking**.
- If you **finished a mask too early** but need to add more, simply **select the object** you want to modify and press `N`.
Alternatively, select the object and click the “Edit nodes” icon (⬟) in the bottom panel.

## Classes

### noteheadWhole
- It does not have an attached stem.
- Fill the entire notehead but **leave out the center**.

![noteheadWhole](./img/notehead-whole-1.png)

---

### noteheadHalf
- Always **leave out the center**. Don’t just outline the shape.

<p>
  <img src="./img/notehead-half-1.png" alt="noteheadHalf example" width="300"/>
  <img src="./img/notehead-half-2.png" alt="noteheadHalf example 2" width="220"/>
</p>

---

### noteheadBlack

*(Previously in CVAT: `notehead_full`. You may find `noteheadFull` in MuNG, but **do NOT use it.**)*

<p>
  <img src="./img/notehead-black-1.png" alt="noteheadBlack Example" width="200"/>
  <img src="./img/notehead-black-2.png" alt="noteheadBlack Example 2" width="175"/>
</p>

---

### augmentationDot

*(Previously in CVAT: `duration_dot`)*

<p>
  <img src="./img/augmentation-dot-1.png" alt="augmentationDot Example" width="200"/>
</p>

---

### stem

<p>
  <img src="./img/stem-1.png" alt="stem Example" width="150"/>
</p>

**TODO:** Zvalidovat: Jan Hajič, [6.řádek, 3.takt](https://ufallab.ms.mff.cuni.cz/~mayer/mung-studio/#/simple-backend/81c9f683-28d1-4e73-8e25-e37333408f5a_4a7de812-b895-4c1b-b785-d4c82f4e243a) - značit jako jednu nožičku?

<p>
  <img src="./img/stem-2.png" alt="stem Example 2" width="150"/>
</p>

---

### flag(number)th(Up/Down)

Flags are divided into separate classes according to their type and direction:

- **flag8thUp** / **flag8thDown**
<p>
  <img src="./img/flag-8th-down-1.png" alt="flag8thUp outer Example" width="220"/>
</p>

- **flag16thUp** / **flag16thDown**  
  ⚠️ *Be careful:* If a single note has **two flags**, the outer is **8th** and the inner is **16th** (and the same for three flags - 8th, 16th, 32nd... and so on).
- **flag32ndUp** / **flag32ndDown**
- *(and so on for higher flag counts)*

⚠️ flag8thUp, flag16thUp
<p>
  <img src="./img/flag-8th-up-1.png" alt="flag8thUp outer Example" width="190"/>
  <img src="./img/flag-16th-up-1.png" alt="flag16thUp inner Example" width="180"/>
</p>

---

### beam

<p>
  <img src="./img/beam-1.png" alt="flag8thUp outer Example" width="290"/>
</p>

---

### legerLine

*(Not “ledger”, both variants are correct ([Wikipedia](https://en.wikipedia.org/wiki/Ledger_line)), but we use leger to stay compliant with SMuFL specification.)*

<p>
  <img src="./img/leger-line-1.png" alt="legerLine Example" width="450"/>
</p>

---

### Grace note (composite)
A grace note is composed of:
- **noteheadWholeSmall / noteheadHalfSmall / noteheadBlackSmall**
<p>
  <img src="./img/notehead-black-small-1.png" alt="noteheadBlackSmall Example" width="350"/>
</p>

- Uses a standard **stem, flag(number)th(Up/Down), beam**

<p>
  <img src="./img/grace-note-1.png" alt="Grace note flag and stem Example" width="350"/>
</p>

- **TODO:** přeškrtnutí zatím nejasné (ornament? předběžně rozseknuto na `graceNoteSlashStemUp`+`graceNoteSlashStemDown`) (tady stará diskuze ke cvatu - https://github.com/orgs/OmniOMR/discussions/61#discussioncomment-9843887) 

---

### tremolo1
- Following SMuFL notation: `tremolo1`
- Multiple tremolo strokes are labeled from **outer to inner** as `tremolo1`, `tremolo2`, `tremolo3`, etc.  (Similar to the `flag` hierarchy.)

- **TODO:** Needs verification. Při převodu z CVAT použito: `tremoloMark`

---

### slur

- Annotate even when the slur appears at the **end of a page** and it’s unclear whether it’s a slur or a tie (see [discussion](https://github.com/orgs/OmniOMR/discussions/108#discussioncomment-13986659)).
- All annotated pages are available in the **Digital Library**, where you can browse the full document. If you want to check it yourself (for clefs or slurs), the links follow this format:

    `https://www.digitalniknihovna.cz/mzk/view/uuid:<document_id>?page=uuid:<page_id>`

<p>
  <img src="./img/slur-1.png" alt="slur Example" width="300"/>
</p>

---

### tie

<p>
  <img src="./img/tie-1.png" alt="tie Example" width="600"/>
</p>

---

### accidentalSharp
*(`sharp` in CVAT)*  
- Always **leave out the center!** Don’t just outline the shape.

<p>
  <img src="./img/accidental-sharp-1.png" alt="accidentalSharp Example" width="200"/>
</p>

---

### accidentalFlat
- Always **leave out the center!** Don’t just outline the shape.

<p>
  <img src="./img/accidental-flag-1.png" alt="accidentalFlat Example" width="200"/>
</p>

---

### accidentalNatural

- Always **leave out the center!** Don’t just outline the shape.

<p>
  <img src="./img/accidental-natural-1.png" alt="accidentalNatural Example" width="150"/>
</p>

---

### fermataAbove / fermataBelow

<p>
  <img src="./img/fermata-above-1.png" alt="fermataAbove Example" width="200"/>
  <img src="./img/fermata-below-1.png" alt="fermataBelow Example" width="183"/>
</p>

---

### fClef

<p>
  <img src="./img/f-clef-1.png" alt="fClef Example" width="200"/>
</p>

---

### fClefChange
- Used when the **clef changes in the middle of the staff** to an F clef.
- These symbols are typically **smaller in size** than standard clefs.
- Make sure to annotate them as **this object**, distinct from the regular clef symbols at the beginning of the staff.

---

### gClef
- Always **leave out the center!** Don’t just outline the shape.

<p>
  <img src="./img/g-clef-2.png" alt="gClef Example" width="135"/>
  <img src="./img/g-clef-1.png" alt="gClef Example" width="140"/>
</p>

---

### gClefChange
- Used when the **clef changes in the middle of the staff** to a G clef.
- These symbols are typically **smaller in size** than standard clefs.
- Make sure to annotate them as **this object**, distinct from the regular clef symbols at the beginning of the staff.

---

### cClef

<p>
  <img src="./img/c-clef-1.png" alt="cClef Example" width="150"/>
</p>

---

### cClefChange
- Used when the **clef changes in the middle of the staff** to a C clef.
- These symbols are typically **smaller in size** than standard clefs.
- Make sure to annotate them as **this object**, distinct from the regular clef symbols at the beginning of the staff.

---

### timeSig[Number 0-9]
- Represents individual **digits** in the time signature (0–9).  
- If the number is **greater than 9**, annotate each digit separately. (For example, a time signature of `10` should be split into **`timeSig1`** and **`timeSig0`**.)
- **TODO:** vyřešit graf

<p>
  <img src="./img/time-sig-1.png" alt="timeSig 6 and 8 Example" width="350"/>
</p>

---

### timeSigFractionalSlash
- Represents the **horizontal line or slash** separating the upper and lower numbers of a time signature.

---

### timeSigFractionalEquals
- Represents the **equals sign (“=”)** used in **fractional or complex time signatures**.

---

### timeSignature
- A **container class** for grouping all elements that form a complete time signature.
- Use it to wrap **either a single object or multiple separate digits** (e.g., 3/4=6/10 as a compact symbol).
- If the time signature appears **at the end of a staff line**, still annotate it as a full `timeSignature` object:

<p>
  <img src="./img/time-signature-1.png" alt="timeSignature Example" width="300"/>
</p>

---

### restWhole

<p>
  <img src="./img/rest-whole-1.png" alt="restWhole Example" width="250"/>
</p>

---

### restHalf

---

### restQuarter

<p>
  <img src="./img/rest-quarter-1.png" alt="restQuarter Example" width="250"/>
</p>

---

### rest8th

<p>
  <img src="./img/rest-8th-1.png" alt="rest8th Example" width="200"/>
</p>

---

### rest16th

<p>
  <img src="./img/rest-16th-1.png" alt="rest16th Example" width="200"/>
</p>

---

### artic(Something)
- previously in CVAT `articulation_mark` for every articulation mark, now separated into classes.

### articAccentAbove / articAccentBelow
- Represents an **accent mark** placed **above or below** the notehead.

### articStaccatoAbove / articStaccatoBelow
- Represents **staccato dots** placed above or below the notehead.
- **Do not use** the old class name `articulationStaccato`.

### articTenutoAbove / articTenutoBelow
### articMarcatoAbove
### articMarcatoBelow

---

### arpeggiato 
*(Previously grouped under `ornament` in CVAT.)*  
- Used for **vertical wavy lines** indicating that a chord should be **arpeggiated**.  
- Note: use the class name **`arpeggiato`**, **not** `arpeggio`.

---

### ornamentTrill
*(Previously grouped under `ornament` in CVAT.)*  
- Used for the **“tr” text** symbol marking a **short trill**.
- Do not use a simple convex hull. The annotation **must follow the exact shape** of the symbol. **TODO:** je toto pravda?

<p>
  <img src="./img/ornament-trill-1.png" alt="ornamentTrill Example" width="200"/>
</p>

---

### wiggleTrill
- Represents the **wavy line** that typically **follows a trill mark**,  
indicating the continuation of the trill.

---

**TODO:** U textů bude potřeba vyřešit jestli texty přepisovat (podobně jako umožňoval CVAT - pozor na nečitelné texty).

### lyricsText
- Annotate **syllable by syllable or separate words**, so that each lyric segment can be correctly aligned with the notation graph.
- It is sufficient to use a **convex hull (rough mask)** for lyrics — precise outlining is not required.

<p>
  <img src="./img/lyrics-text-1.png" alt="lyricsText Example" width="400"/>
</p>

### dynamicsText
- Represents a **textual region** covering one or more **dynamic marks**.
- The **specific dynamic symbol** (e.g., `p`, `f`, `ff`) should be annotated **precisely** using its respective `dynamicXXX` class.  
- The surrounding **text region** should then be annotated as `dynamicsText`, using a **convex hull** that encloses all relevant symbols.

**Examples:**
- For a single “p” (piano), mark:
  - `dynamicPiano` — exact symbol outline  
  - `dynamicsText` — convex hull enclosing it
- For “ff” (fortissimo), mark:
  - Two symbols: `dynamicForte` + `dynamicForte`
  - One `dynamicsText` area enclosing both

### `dynamic<Symbol>` (precise masks)
The following classes must be annotated **accurately (not convex)**:
- `dynamicForte`
- `dynamicMezzo`
- `dynamicNiente`
- `dynamicPiano`
- `dynamicRinforzando`
- `dynamicSforzando`
- `dynamicZ`

Also remember to add a `dynamicsText` convex hull over these symbols.

> Combined markings such as `po` or `p:` should be annotated as a **single** `dynamicPiano` object.

### tempoText
- **TODO:** Define rules for tempo markings (e.g. “Pochodem”, “Allegro”, etc.)

### otherText
Used for **non-musical text elements** such as:
- Page numbers  
- Titles  
- Verse numbers

---

### systemDivider
*(Called `system_break` in CVAT)* 

---

### brace
- Represents the **curly bracket `{`** used to connect multiple staves belonging to a single instrument (e.g., piano).  
- Corresponds to `staff_bracket` in CVAT.  
- Usually connects **two staves**, but can occasionally span **three** (e.g., in organ notation).

<p>
  <img src="./img/brace-1.png" alt="brace Example" width="150"/>
</p>

---

### bracket
- Represents the **square bracket `[`** used to group staves (e.g., for instrument families in orchestral scores).  
- ⚠️ **Important:** a second vertical line often appears near the bracket, but that line **is not part of the bracket**. It should be annotated separately as `barlineSingle`.

<p>
  <img src="./img/bracket-1.png" alt="bracket Example" width="300"/>
</p>

---

### barlineSingle
*(Called `thin_barline` in CVAT)*  
- Represents a **single thin barline**.  
- Annotate **precisely around the entire shape**.

<p>
  <img src="./img/barline-single-1.png" alt="barlineSingle Example" width="180"/>
</p>

---

### barlineHeavy
*(Called `barline_thick` in CVAT)*
- Represents a **thick barline**, usually used at section endings

<p>
  <img src="./img/barline-heavy-1.png" alt="barlineHeavy Example" width="250"/>
</p>

---

### staff1Line
*(Called `Staff line` in CVAT)*  
- Represents a **single staff line**.
- Annotate **precisely around the entire shape**.

<p>
  <img src="./img/staff-1-line.png" alt="staff1Line Example" width="700"/>
</p>

---

### staff
- shlukuje 5 linek
- potřeba, aby sedělo přesně na rohy
- těsný box čar

---

### staffGrouping
- abstraktní shlukovač
- obskurnější staff grouping https://github.com/orgs/OmniOMR/discussions/108#discussioncomment-13698771 
- pravidla ke staff grouping https://github.com/orgs/OmniOMR/discussions/91#discussion-7177410 

### measureSeparator

### keySignature

### repetice se skládá z:
#### repeat
- maska
#### bracket/barlineSingle/barlineHeavy
#### repeatDot

### splitBarDivider
- napojení taktu (ta vlnovka na konci)

### repeat1Bar
- CVAT repeat_measure_sign

### unclassified
- TODO: rozseknout, jestli je tahle kategorie potřeba a při jekých situacích
- CVAT ufo
- prosaky není potřeba řešit, pokud vyloženě neiterferujíc s notací (tzn. člověk by si špatně mohl vyložit)
- vlasy, rozlitý kafe, rozpláclý mouchy dělám jako ufo area (ale dávám to jen tam, kde to zasahuje do not/osnov, zkrátka do čtení textu)
- NEZNAČIT: hřbety knih a notaci na sousední stránce, věci které nevím jak značit (pokud nevím, zeptat se), symboly z předchozích stránek
- prosak, co nevypadá jako by byl v popředí (takový duch) - udělat screen: https://ufallab.ms.mff.cuni.cz/~mayer/mung-studio/#/simple-backend/81c9f683-28d1-4e73-8e25-e37333408f5a_4a7de812-b895-4c1b-b785-d4c82f4e243a

### figuredBassText
- konvexní obal skupinky

### TODO: figured_bass_spanner
- zatím pro to není třída

### TODO: “=”
- TODO: není pro to maska - je to asi podobně rozšířené jako repeat_measure_sign!!! POTŘEBA VYŘEŠIT
- dvě čáry - Píšou se, když má nástroj hrát unisono s jiným partem

### TODO když se vyskytne
repetice, takže vlnovky jako repeat_dot, šikmé dvojčárky možná jako "other" - taková ta divná repetice - voláme výš, tohle je potřeba dořešit

`%` teď jsem našla, že asi Vojta to převádí ze CVATu do `repeatOneBar`


další symboly co lze najít ve vyhledávání jsou pro kompatibilitu s jinýma datasetama - není pro anotátory - pokud tady není zaznačený znak, neznačit nějakým vymyšleným z možností, ale doptat se
