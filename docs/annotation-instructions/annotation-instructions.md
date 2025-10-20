
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

- **TODO:** Needs verification.

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



---

### accidentalFlat
- Always **leave out the center!** Don’t just outline the shape.

### accidentalNatural

### fermataAbove

### fermataBelow

### fClef

### fClefChange

### gClef
- vynechávat prostředky! nedělat jen obal!

### gClefChange

### cClef

### cClefChange


### timeSig[Number 0-9]
- if number > 9, then mark it via numerals (e.g. 10 is divided into timeSig1 and timeSig0)
TODO: vyřešit graf

### timeSignature
- obalovač
- obalit i jeden objekt, nebo i víc ¾=6/10, pak obalit celé
- může být i na konci řádku (screen 7. řádek)

### timeSigFractionalSlash
- vodorovná čára nebo lomítko oddělující horní a dolní číslo

### timeSigFractionalEquals


### restWhole

### restQuarter

### rest8th

### rest16th
...

### articAccentAbove
### articAccentBelow
### articStaccatoAbove
- do NOT use articulationStaccato
### articStaccatoBelow
### articTenutoAbove
### articTenutoBelow
### articMarcatoAbove
### articMarcatoBelow

### arpeggiato 
- ne arpeggio
### ornamentTrill
- tr text, pokud je to krátký trylek

### wiggleTrill
- typicky jako čára za tr

### lyricsText
- vyscreenovat https://ufallab.ms.mff.cuni.cz/~mayer/mung-studio/#/simple-backend/4b494e80-4cd2-11ea-a3ba-005056827e52_c98a8dd2-1141-48c8-a594-ee15db270b02
- vyscreenovat https://ufallab.ms.mff.cuni.cz/~mayer/mung-studio/#/simple-backend/4b494e80-4cd2-11ea-a3ba-005056827e52_89218983-dac6-4e8f-9549-05f18d613154
- dělat po slabikách / tak aby se dalo navázat na notační graf
- stačí konvexní obal (hrubá maska)

### dynamicsText
- maska nad dynamicTextem
- třeba piano `p` bude `dynamicPiano` značený přesně a `dynamicsText` nad tím jako konvexní obal.
- ff budou dva symboly `dynamicForte` a nad tím bude `dynamicsText` jako konvexní obal.

#### dynamicsXXX značené přesně
- `dynamicForte`, `dynamicMezzo`, `dynamicNiente`, `dynamicPiano`, `dynamicRinforzando`, `dynamicSforzando`, `dynamicZ`
- a nad tím nezapomenout na `dynamicsText jako konvexní obal`
- `po`, `p:` značit celé jako jeden `dynamicPiano`

### tempoText
TODO: Pochodem. ????

### otherText
- číslo stránky, nadpis, číslo sloky

### systemDivider
- v CVAT system_break
- systemSeparator neee

### brace
- `{` složená
- staff_bracket ve cvatu
- spojit více osnov pro jeden nástroj - např. piano
- někdy může být i přes tři osnovy, ale výjimečné (u varhan třeba)

### bracket
- hranatá `[`
- udělat screen - https://ufallab.ms.mff.cuni.cz/~mayer/mung-studio/#/simple-backend/81c9f683-28d1-4e73-8e25-e37333408f5a_4a7de812-b895-4c1b-b785-d4c82f4e243a
- pozor, často u bracket bývá druhá čára, která ale už bracket není a má se značit jako `barlineSingle`

### barlineSingle
- CVAT thin_barline

### barlineHeavy
- tlustá čára
- CVAT barline_thick

### staff1Line
- CVAT Staff line
- 1 linka

### staff
- shlukuje 5 linek
- potřeba, aby sedělo přesně na rohy
- těsný box čar

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


další symboly co lze najít ve vyhledávání jsou pro kompatibilitu s jinýma datasetama - není pro anotátory - pokud tady není zaznačený znak, neznačit nějakým vymyšleným z možností, ale doptat se
