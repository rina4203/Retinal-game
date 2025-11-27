import json

# --- 1. Twinkle Twinkle ---
twinkle_twinkle = [
    'c4','c4','g4','g4','a4','a4','g4',
    'f4','f4','e4','e4','d4','d4','c4',
    'g5','g5','f4','f4','e4','e4','d4',
    'g5','g5','f4','f4','e4','e4','d4',
    'c4','c4','g4','g4','a4','a4','g4',
    'f4','f4','e4','e4','d4','d4','c4',
]

# --- 2. Happy Birthday ---
happy_birthday = [
    "g4", "g4", "a4", "g4", "c5", "b4",
    "g4", "g4", "a4", "g4", "d5", "c5",
    "g4", "g4", "g5", "e5", "c5", "b4", "a4",
    "f5", "f5", "e5", "c5", "d5", "c5"
]

# --- 3. Billie Eilish - Birds of a Feather (Full Structure) ---
# Частини мелодії:
billie_verse = [
    "f#4", "a4", "b4", "a4", "f#4", "e4", "d4", # I want you to stay
    "e4", "f#4", "e4", "d4", "b3",               # Till I'm in the grave
    "d4", "e4", "f#4", "a4", "b4", "a4",         # Till I rot away, dead and buried
    "f#4", "e4", "d4", "b3"                      # Till I'm in the casket you carry
]

billie_chorus = [
    "f#4", "f#4", "e4", "d4",        # Birds of a feather
    "f#4", "f#4", "e4", "d4",        # We should stick together
    "f#4", "e4", "d4", "b3", "a3",   # I know I said I'd never...
    "b3", "d4", "e4",                # ...think I wasn't better alone
    "f#4", "f#4", "e4", "d4",        # Can't change the weather
    "f#4", "f#4", "e4", "d4",        # Might not be forever
    "f#4", "e4", "d4", "b3", "a3",   # But if it's forever...
    "b3", "d4", "e4"                 # ...it's even better
]

# Збираємо повну пісню: Куплет + Приспів + Куплет + Приспів
birds_of_a_feather_full = billie_verse + billie_chorus + billie_verse + billie_chorus


# --- 4. Adele - Rolling in the Deep (Full Structure) ---
# Частини мелодії (Тональність Do minor / C minor):

adele_verse = [
    "c4", "c4", "g3", "a#3", "g#3", "g3",  # There's a fire starting in my heart
    "g#3", "g#3", "g#3", "a#3", "g#3", "g3", "f3", # Reaching a fever pitch...
    "c4", "c4", "g3", "a#3", "g#3", "g3",  # Finally I can see you crystal clear
    "g#3", "g#3", "g#3", "a#3", "g#3", "g3" # Go ahead and sell me out...
]

adele_pre_chorus = [
    "f3", "f3", "g3", "g#3", "a#3",        # The scars of your love remind me of us
    "g#3", "g3", "f3", "g#3", "g3",        # They keep me thinking that we almost had it all
    "f3", "f3", "g3", "g#3", "a#3",        # The scars of your love...
    "c4", "a#3", "g#3", "g3"               # ...leave me breathless
]

adele_chorus = [
    "g4", "g4", "g4", "g4", "g#4", "a#4", # We could have had it all
    "g4", "g4", "f4", "g4",               # Rolling in the deep
    "g4", "f4", "d#4", "d4", "c4",        # You had my heart inside of your hand
    "a#3", "c4", "d4", "d#4", "d4", "c4", # And you played it to the beat
    "g4", "g4", "g4", "g4", "g#4", "a#4", # (Repeat) We could have had it all
    "g4", "g4", "f4", "g4"                # Rolling in the deep
]

# Збираємо повну пісню: Куплет + Перехід + Приспів + Куплет + Перехід + Приспів
rolling_in_the_deep_full = adele_verse + adele_pre_chorus + adele_chorus + adele_verse + adele_pre_chorus + adele_chorus


# --- Формування JSON ---
notes = {
    '1' : twinkle_twinkle,
    '2' : happy_birthday,
    '3' : birds_of_a_feather_full,
    '4' : rolling_in_the_deep_full
}

with open('notes.json', 'w') as file:
    json.dump(notes, file)

print("Файл notes.json оновлено. Додано повні версії пісень.")