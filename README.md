# runesmith
Python-based application to automate rune forging in Pox Nora.

Currently in very early development.

To try runesmith for yourself, check the [releases](https://github.com/discomethod/runesmith/releases).

### FAQ
##### Are you harvesting my username and password to steal my account?
No. Your username and password are sent directly to the Pox Nora servers and are not saved anywhere.
##### Will runesmith trade you all my runes for a Bronze token?
No. Runesmith does not do any trading via the Rune Trader. It only handles transactions with the Rune Forge, where you trade in runes for nora and can forge runes from nora.
##### What's the point of using runesmith when I can trade the runes in myself?
Runesmith is a lot faster and easier. If you have loads of commons and uncommons lying around in your inventory, it's annoying to click through the Sacrifice -> Confirm -> Wait -> Repeat thousands of times. Plus, runesmith will give you a quote of how much nora you can expect to make by trading in all your excess runes - without actually doing so.
##### Can I use runesmith to forge myself 2 of every common?
Not yet - however, that may come in the future.
##### How do I use runesmith?
See above on how to download the latest release. Once you've extracted all the files, you should in theory only need to run two commands to trade in all your runes:

```python
import crawler
crawler.do_login('my_username','my_password')
crawler.do_trade_in_batch()
```
Note that you will need to have Python 2.7 installed to run the current version. An executable version may be released in the future.
