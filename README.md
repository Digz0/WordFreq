# Word Rarity Analyzer

Word Rarity Analyzer is a Python tool that calculates the rarity of words in a given text. It uses the Zipf frequency from the wordfreq library to determine how common or rare a word is in a specified language.

## Features

- Calculate rarity scores for individual words
- Analyze the rarity of all words in a given text
- Support for multiple languages
- Interactive command-line interface

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/word-rarity-analyzer.git
   cd word-rarity-analyzer
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv wordfreq_env
   source wordfreq_env/bin/activate  # On Windows, use `wordfreq_env\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script interactively:
```
python word_rarity_analyzer.py
```

Follow the prompts to enter your text and specify the language.

## How it works

The tool uses the Zipf frequency scale, which typically ranges from 0 (very rare) to 7 (very common). This scale is inverted and adjusted to a 0-8 scale, where:

- 0 represents very common words
- 8 represents very rare words or numbers

## Supported Languages

The tool supports all languages available in the wordfreq library. Use the appropriate language code when prompted (e.g., 'en' for English, 'fr' for French).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.