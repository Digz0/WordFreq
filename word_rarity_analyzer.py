# Import the zipf_frequency function from the wordfreq library
from wordfreq import zipf_frequency, available_languages
# Import the re module for regular expressions
import re
import unicodedata

def word_rarity(word, language='en'):
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

def analyze_rarity(text, language='en', max_length=100000):
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

# Wrap the main logic in a function
def main():
    # Prompt user for input
    print("Please paste your text below and press Enter twice when you're done:")
    # Initialize an empty list to store user input
    user_input = []
    # Loop to collect multi-line input
    while True:
        line = input()
        if line == "":
            break
        user_input.append(line)

    # Join the input lines into a single string
    text_to_analyze = " ".join(user_input)
    if not text_to_analyze.strip():
        print("Error: Empty input")
        return

    print("Enter the language code (e.g., 'en' for English, 'fr' for French):")
    language = input().strip()

    try:
        results, avg_rarity = analyze_rarity(text_to_analyze, language)

        print("\nRarity Analysis Results:")
        print(f"Average Rarity Score: {avg_rarity:.2f}")
        print("\nIndividual Word Scores:")
        for word, rarity in results:
            print(f"Word: {word} | Rarity Score: {rarity:.2f}")
    except ValueError as e:
        print(f"Error: {str(e)}")
        return  # Exit the function after printing the error

# Only run the main function if this script is run directly
if __name__ == "__main__":
    main()