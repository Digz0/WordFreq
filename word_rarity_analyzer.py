# Import the zipf_frequency function from the wordfreq library
from wordfreq import zipf_frequency, available_languages
# Import the re module for regular expressions
import re
import unicodedata
# Add these imports at the top of the file
import logging
from typing import List, Tuple
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add logging statements in the functions
def word_rarity(word: str, language: str = 'en') -> float:
    logging.debug(f"Calculating rarity for word: {word} in language: {language}")
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
    
    # Normalize Unicode characters
    word = unicodedata.normalize('NFKC', word)
    
    # Check if the word contains only digits
    if re.match(r'^\d+$', word):
        return 8  # Return maximum rarity for numbers
    
    # Very long words are likely rare
    if len(word) > 50:
        return 8
    
    # Get the Zipf frequency of the word
    zipf = zipf_frequency(word, language)
    
    # Convert Zipf frequency to rarity score
    # Zipf scale typically ranges from 0 (very rare) to 7 (very common)
    # We'll invert this so that higher scores mean rarer words
    rarity_score = 8 - zipf
    
    # Return the calculated rarity score
    return max(0, min(rarity_score, 8))  # Ensure the score is between 0 and 8

def analyze_rarity(text: str, language: str = 'en', max_length: int = 100000) -> Tuple[List[Tuple[str, float]], float]:
    logging.info(f"Analyzing text of length {len(text)} in language: {language}")
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
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFKC', text)
    
    # Update regex to include only alphabetic words (including Unicode letters)
    words = re.findall(r'\b[^\W\d_]+\b', text.lower(), re.UNICODE)
    word_rarity_dict = {}
    
    for word in set(words):
        rarity = word_rarity(word, language)
        word_rarity_dict[word] = rarity

    sorted_results = sorted(word_rarity_dict.items(), key=lambda x: (-x[1], x[0]))
    total_rarity = sum(word_rarity_dict.values())
    avg_rarity = total_rarity / len(word_rarity_dict) if word_rarity_dict else 0
    
    return sorted_results, avg_rarity

def main(file_path=None, language="en", text=None):
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