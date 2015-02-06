LEVEL_TO_KEEP = 2 # any champion runes this level or above will not be traded in

# --- VERIFY SETTINGS --- #

if not isinstance(LEVEL_TO_KEEP, int) or not 3 >= LEVEL_TO_KEEP >= 1:
    raise AssertionError("LEVEL_TO_KEEP must be an integer between 1 and 3. Current setting is {0}".format(LEVEL_TO_KEEP))
