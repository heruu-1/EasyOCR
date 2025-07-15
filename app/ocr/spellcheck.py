from spellchecker import SpellChecker
import os

SPELL = SpellChecker(language=None, case_sensitive=False)
try:
    kamus_path = os.path.join(os.path.dirname(__file__), 'kamus_indonesia.txt')
    SPELL.word_frequency.load_text_file(kamus_path)
    print(f"Kamus Indonesia berhasil dimuat dari: {kamus_path}")
except Exception as e:
    print(f"Error memuat kamus Indonesia: {e}")

def correct_spelling(text):
    corrected_words = []
    for w in text.split():
        if w not in SPELL:
            correction = SPELL.correction(w)
            if correction:  # Pastikan correction tidak None
                corrected_words.append(correction)
            else:
                corrected_words.append(w)  # Gunakan kata asli jika tidak ada koreksi
        else:
            corrected_words.append(w)
    return ' '.join(corrected_words)
