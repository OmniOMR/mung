
připsat, že pravým tlačítkem lze u vytváření polygonu skočit o jeden bod dozadu

ukončila jsem masku brzo, ale potřebuji něco přidat, co s tím? stačí vybrat objekt ke kterému chci přidávat a zmáčknout `N`. Případně vybrat objekt a v dolním okénku `Edit nodes` (pětiúhelník).

## Classes

### noteheadWhole
- celá nota, vynechávat střed
- není k ní attached nožička

### noteheadHalf
- vždycky vynechávat prostředky!!! nedělat jen obal!!!

### noteheadBlack

(previously in CVAT `notehead_full`, you can find `noteheadFull` in MuNG, but do NOT use it)

### augmentationDot

(previously `duration_dot`)

### stem


### Grance note
Composed of:

#### noteheadHalfSmall

#### noteheadBlackSmall

obyčejný stem, flag, beam, přeškrtnutí zatím nejasné (ornament zatím, tak zpět, rozseknuto na `graceNoteSlashStemUp`+`graceNoteSlashStemDown` - nikde to není standardizované) (tady stará diskuze ke cvatu - https://github.com/orgs/OmniOMR/discussions/61#discussioncomment-9843887) 

### flag
rozdělený do tříd
8th up/down
16th up/down - tady catch - když 2flags u jedné noty, tak jedna 8th, druhá 16th (zvnějšku)
32th ...
#### flag8thUp


### beam

### legerLine
(not ledger - yes both variants valid [https://en.wikipedia.org/wiki/Ledger_line](Wikipedia), in cvat ledger, now leger to be compliant with SMuFL)

### tremolo
we use SMuFL, so tremolo1
more tremolo, outer to inner tremolo1,tremolo2,tremolo3,... (similar to flag principle)
TODO: potřeba zkontrolovat vyšší mocí

### slur
dávat i když je na konci stránky a není jasné, jestli to je tie nebo slur (viz [https://github.com/orgs/OmniOMR/discussions/108#discussioncomment-13986659](zde)), Ale je možnost navazující stránku dohledat (jako dohledáváme klíče v MuseScore). Všechny anotované stránky jsou v Digitální knihovně, kde se dá listovat celým dokumentem. Kdybyste to chtěli dohledávat sami (třeba i kvůli těm klíčům), odkazy vypadají takhle: https://www.digitalniknihovna.cz/mzk/view/uuid:5c5a6d8c-b434-4496-a9ac-67d518230273?page=uuid:858b1bb0-c001-427c-95b0-a3ee0ad1b3bc (to je 1. obrázek v tabulce obrázků ze CVATu). Takže vždycky "...view/uuid:[číslo před podtržítkem]?page=uuid:[číslo po podtržítku]".

### tie

### accidentalSharp
(sharp in CVAT)
- vždycky vynechávat prostředky!!! nedělat jen obal!!!

### accidentalFlat
- vždycky vynechávat prostředky!!! nedělat jen obal!!!

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

### TODO: “=”
- TODO: není pro to maska - je to asi podobně rozšířené jako repeat_measure_sign!!! POTŘEBA VYŘEŠIT
- dvě čáry - Píšou se, když má nástroj hrát unisono s jiným partem

### TODO když se vyskytne
repetice, takže vlnovky jako repeat_dot, šikmé dvojčárky možná jako "other" - taková ta divná repetice - voláme výš, tohle je potřeba dořešit


další symboly co lze najít ve vyhledávání jsou pro kompatibilitu s jinýma datasetama - není pro anotátory - pokud tady není zaznačený znak, neznačit nějakým vymyšleným z možností, ale doptat se
