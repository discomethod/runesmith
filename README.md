# runesmith
Python-based application to automate rune forging in Pox Nora.

Currently in very early development.

## Important Notes for Developers

### Pox Nora JSON Data:
####Rarities
* 0: {id: 0, value: "Common"}
* 1: {id: 1, value: "Uncommon"}
* 2: {id: 2, value: "Rare"}
* 3: {id: 3, value: "Exotic"}
* 4: {id: 5, value: "Legendary"}

####Base Rarities
Base rarities are only unique for each rune type (champion, spell, relic, or equipment). For example, Abomination, Draconic Benediction, and Ice Statue all have 'baseId' value of 18.
