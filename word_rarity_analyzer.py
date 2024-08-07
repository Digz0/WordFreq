from wordfreq import zipf_frequency, available_languages
import re
import unicodedata
from typing import List, Tuple
import argparse

def word_rarity(word: str, language: str = 'en') -> float:
    """
    Calculate the rarity score of a given word.

    Args:
    word (str): The word to analyze.
    language (str): The language code (default: 'en' for English).

    Returns:
    float: A rarity score between 0 (very common) and 8 (very rare).

    Raises:
    ValueError: If the language is not supported.
    """
    if language not in available_languages():
        raise ValueError(f"Unsupported language: {language}")
    
    word = unicodedata.normalize('NFKC', word)
    
    if re.match(r'^\d+$', word):
        return 8  # Maximum rarity for numbers
    
    if len(word) > 50:
        return 8  # Very long words are likely rare
    
    zipf = zipf_frequency(word, language)
    
    # Convert Zipf frequency to rarity score (invert scale)
    rarity_score = 8 - zipf
    
    return max(0, min(rarity_score, 8))

def analyze_rarity(text: str, language: str = 'en', max_length: int = 100000) -> Tuple[List[Tuple[str, float]], float]:
    """
    Analyze the rarity of words in a given text.

    Args:
    text (str): The text to analyze.
    language (str): The language code (default: 'en' for English).
    max_length (int): Maximum allowed length of input text.

    Returns:
    tuple: A tuple containing:
        - list of tuples: (word, rarity_score) sorted by rarity (highest to lowest).
        - float: Average rarity score of all words.

    Raises:
    ValueError: If the language is not supported or text is too long.
    """
    if language not in available_languages():
        raise ValueError(f"Unsupported language: {language}")
    
    if len(text) > max_length:
        raise ValueError(f"Input text is too long. Maximum allowed length is {max_length} characters.")
    
    text = unicodedata.normalize('NFKC', text)
    
    # Find all alphabetic words (including Unicode letters)
    words = re.findall(r'\b[^\W\d_]+\b', text.lower(), re.UNICODE)
    word_rarity_dict = {word: word_rarity(word, language) for word in set(words)}

    sorted_results = sorted(word_rarity_dict.items(), key=lambda x: (-x[1], x[0]))
    avg_rarity = sum(word_rarity_dict.values()) / len(word_rarity_dict) if word_rarity_dict else 0
    
    return sorted_results, avg_rarity

def main(file_path=None, language="en", text=None):
    """
    Main function to handle input and display results of word rarity analysis.
    """
    if file_path:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    elif text is None:
        print("Please paste your text below and press Enter twice when you're done:")
        text = "\n".join(iter(input, ""))

    if not text.strip():
        print("Error: Empty input")
        return

    try:
        results, avg_rarity = analyze_rarity(text, language)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return

    print(f"\nAverage Rarity Score: {avg_rarity:.2f}")
    print("\nAll Words Sorted by Rarity:")
    for word, rarity in results:
        print(f"Word: {word} | Rarity Score: {rarity:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze word rarity in a given text.")
    parser.add_argument("--file", help="Path to a text file to analyze")
    parser.add_argument("--language", default="en", help="Language code (default: en)")
    args = parser.parse_args()
    main(file_path=args.file, language=args.language)