import unittest
from word_rarity_analyzer import word_rarity, analyze_rarity
import io
import sys
import importlib
from wordfreq import available_languages
import time
import random

class TestWordRarityAnalyzer(unittest.TestCase):

    def test_word_rarity(self):
        # Test common English words
        self.assertLess(word_rarity('the'), 2)
        self.assertLess(word_rarity('and'), 2)
        self.assertLess(word_rarity('is'), 2)
        
        # Test rare English words
        self.assertGreater(word_rarity('quixotic'), 5)
        self.assertGreater(word_rarity('ephemeral'), 5)
        self.assertGreater(word_rarity('serendipity'), 5)

        # Test non-English words
        if 'fr' in available_languages():
            self.assertGreater(word_rarity('bonjour', 'fr'), 2)  # French word
        if 'de' in available_languages():
            self.assertGreater(word_rarity('schmetterling', 'de'), 2)  # German word
        if 'ja' in available_languages():
            try:
                self.assertGreater(word_rarity('こんにちは', 'ja'), 2)  # Japanese word
            except ModuleNotFoundError:
                print(f"Skipping Japanese word test due to missing MeCab module on {sys.platform}")
        else:
            print("Skipping Japanese word test as 'ja' is not in available languages")

        # Test edge cases
        self.assertEqual(word_rarity(''), 8)  # Empty string
        self.assertEqual(word_rarity('thisisaverylongwordthatprobablydoesntexist'), 8)  # Very long word
        self.assertLess(word_rarity('a'), 2)  # Single letter word

        # Test numbers and special characters
        self.assertEqual(word_rarity('123'), 8)  # Numbers
        self.assertEqual(word_rarity('!@#'), 8)  # Special characters
        self.assertGreater(word_rarity('word123'), 5)  # Combination of letters and numbers

    def test_analyze_rarity(self):
        # Test with a short sentence containing common words
        text = "The quick brown fox jumps over the lazy dog"
        results, avg_rarity = analyze_rarity(text)
        self.assertEqual(len(results), 8, f"Expected 8 unique words, but got {len(results)} for text: '{text}'")
        self.assertTrue(0 < avg_rarity < 4)  # Common words should have lower rarity

        # Test with a sentence containing rare words
        text = "The quixotic physicist pondered the ephemeral nature of serendipity"
        results, avg_rarity = analyze_rarity(text)
        self.assertTrue(len(results) > 0)
        self.assertGreater(avg_rarity, 3)  # Rare words should have higher rarity, but be more flexible
        
        # Check individual rare words
        rare_words = ['quixotic', 'ephemeral', 'serendipity']
        for word, rarity in results:
            if word in rare_words:
                self.assertGreater(rarity, 5, f"Expected {word} to have rarity > 5, but got {rarity}")

        # Test with an empty string
        results, avg_rarity = analyze_rarity("")
        self.assertEqual(len(results), 0)
        self.assertEqual(avg_rarity, 0)

        # Test with a long paragraph
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        results, avg_rarity = analyze_rarity(text)
        self.assertTrue(len(results) > 50)  # Should have many unique words
        self.assertTrue(0 < avg_rarity < 8)

        # Test with text containing numbers and special characters
        text = "Hello, World! 123 Test. @#$%^&*"
        results, avg_rarity = analyze_rarity(text)
        self.assertEqual(len(results), 3)  # Should count 'hello', 'world', and 'test'
        self.assertTrue(0 < avg_rarity < 8)

        # Verify specific words
        words = [word.lower() for word, _ in results]
        self.assertIn('hello', words)
        self.assertIn('world', words)
        self.assertIn('test', words)
        self.assertNotIn('123', words)  # Ensure numbers are not included

        # Test with non-English text (assuming 'fr' is available)
        if 'fr' in available_languages():
            text = "Bonjour le monde"
            results, avg_rarity = analyze_rarity(text, language='fr')
            self.assertEqual(len(results), 3)
            self.assertTrue(0 < avg_rarity < 8)

        # Additional checks
        for text, expected_words in [
            ("The quick brown fox jumps over the lazy dog", 8),
            ("Hello, World! This is a Test.", 6),
            ("Unique words only: one two three four five", 8),
            ("Repeated words: the the the a a an an", 5)
        ]:
            results, _ = analyze_rarity(text)
            self.assertEqual(len(results), expected_words, f"Expected {expected_words} unique words, but got {len(results)} for text: '{text}'")
            
            # Check if results are sorted by rarity (highest to lowest)
            rarities = [rarity for _, rarity in results]
            self.assertEqual(rarities, sorted(rarities, reverse=True))
            
            # Check rarity bounds
            for _, rarity in results:
                self.assertTrue(0 <= rarity <= 8)
            
            # Check for unique words
            words = [word for word, _ in results]
            self.assertEqual(len(words), len(set(words)), f"Duplicate words found in results for text: '{text}'")

        # Add a specific test for this case
        text = "Unique words only: one two three four five"
        results, _ = analyze_rarity(text)
        expected_words = ['unique', 'words', 'only', 'one', 'two', 'three', 'four', 'five']
        actual_words = [word for word, _ in results]
        self.assertSetEqual(set(expected_words), set(actual_words), f"Expected words {expected_words}, but got {actual_words}")

        # Add a specific test for repeated words
        text = "Repeated words: the the the a a an an"
        results, _ = analyze_rarity(text)
        expected_words = ['repeated', 'words', 'the', 'a', 'an']
        actual_words = [word for word, _ in results]
        self.assertSetEqual(set(expected_words), set(actual_words), f"Expected words {expected_words}, but got {actual_words}")

    def run_integration_test(self, test_input, expected_outputs, language="en"):
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            word_rarity_analyzer = importlib.import_module('word_rarity_analyzer')
            word_rarity_analyzer.main(text=test_input, language=language)
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        for expected in expected_outputs:
            self.assertIn(expected, output)

    def test_integration(self):
        # Test with empty input
        self.run_integration_test("", ["Error: Empty input"])

        # Test with punctuation and numbers
        self.run_integration_test("Hello, World! 123 Test.", 
                                  ["Average Rarity Score:", 
                                   "Word: hello |",
                                   "Word: world |",
                                   "Word: test |"])

        # Test with mixed common and rare words
        self.run_integration_test("The quick brown fox jumps over the lazy dog, while a quixotic physicist ponders.",
                                  ["Average Rarity Score:",
                                   "All Words Sorted by Rarity:",
                                   "Word: quixotic |",
                                   "Word: physicist |",
                                   "Word: ponders |",
                                   "Word: brown |",
                                   "Word: jumps |",
                                   "Word: quick |",
                                   "Word: while |",
                                   "Word: lazy |",
                                   "Word: over |",
                                   "Word: fox |",
                                   "Word: dog |",
                                   "Word: the |",
                                   "Word: a |"])

        # Test sorting of results (should be sorted by rarity, highest to lowest)
        output = self.get_integration_output("Common rare unique words.")
        print("Full output:")
        print(output)
        lines = output.split('\n')
        rarity_scores = [float(line.split(': ')[-1]) for line in lines if 'Rarity Score:' in line and 'Average' not in line]
        print("Extracted rarity scores:", rarity_scores)
        self.assertEqual(rarity_scores, sorted(rarity_scores, reverse=True), 
                         f"Results should be sorted by rarity (highest to lowest). Got: {rarity_scores}")

        # Test for words with equal rarity scores (should be sorted alphabetically)
        output = self.get_integration_output("apple banana cherry date.")
        lines = output.split('\n')
        word_scores = []
        for line in lines:
            if '|' in line and 'Rarity Score:' in line:
                parts = line.split('|')
                word = parts[0].split(':')[1].strip()
                score = float(parts[1].split(':')[1].strip())
                word_scores.append((word, score))
        
        self.assertEqual(word_scores, sorted(word_scores, key=lambda x: (-x[1], x[0])),
                         f"Results should be sorted by rarity and then alphabetically. Got: {word_scores}")

        # Test average rarity calculation
        output = self.get_integration_output("The quick brown fox.")
        avg_rarity_line = next(line for line in output.split('\n') if 'Average Rarity Score:' in line)
        avg_rarity = float(avg_rarity_line.split(': ')[-1])
        self.assertTrue(0 < avg_rarity < 8, f"Average rarity {avg_rarity} should be between 0 and 8")

    def get_integration_output(self, test_input):
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            word_rarity_analyzer = importlib.import_module('word_rarity_analyzer')
            word_rarity_analyzer.main(text=test_input, language="en")
        finally:
            sys.stdout = sys.__stdout__

        return captured_output.getvalue()

    def test_invalid_language(self):
        with self.assertRaises(ValueError):
            word_rarity('hello', 'invalid_language')
        
        with self.assertRaises(ValueError):
            analyze_rarity('Hello world', 'invalid_language')

    def test_extremely_long_input(self):
        very_long_text = "word " * 50001  # 250,005 characters
        with self.assertRaises(ValueError):
            analyze_rarity(very_long_text)

    def test_word_rarity_error_handling(self):
        # Test with an unsupported language
        with self.assertRaises(ValueError):
            word_rarity('hello', 'unsupported_lang')

        # Test with a very long word
        very_long_word = 'a' * 1000
        result = word_rarity(very_long_word)
        self.assertEqual(result, 8)  # Should return max rarity for very long words

    def test_analyze_rarity_error_handling(self):
        # Test with an unsupported language
        with self.assertRaises(ValueError):
            analyze_rarity("Hello world", 'unsupported_lang')

        # Test with an empty string
        results, avg_rarity = analyze_rarity("")
        self.assertEqual(len(results), 0)
        self.assertEqual(avg_rarity, 0)

        # Test with only numbers and special characters
        results, avg_rarity = analyze_rarity("123 !@# 456")
        self.assertEqual(len(results), 0)
        self.assertEqual(avg_rarity, 0)

        # Test with an unsupported language
        with self.assertRaises(ValueError):
            analyze_rarity("Hello world", 'unsupported_lang')

    def test_integration_error_handling(self):
        # Test with invalid language
        self.run_integration_test("Hello world", 
                                  ["Error: Unsupported language: invalid_lang"],
                                  language="invalid_lang")

        # Test with extremely long input
        very_long_input = "word " * 20001
        self.run_integration_test(very_long_input, 
                                  ["Error: Input text is too long. Maximum allowed length is 100000 characters."])

    def test_user_interface(self):
        test_input = "This is a\nmulti-line\ninput test"
        captured_output = io.StringIO()
        sys.stdout = captured_output

        try:
            word_rarity_analyzer = importlib.import_module('word_rarity_analyzer')
            word_rarity_analyzer.main(text=test_input, language="en")
        finally:
            sys.stdout = sys.__stdout__

        output = captured_output.getvalue()

        # Verify results are displayed
        self.assertIn("Average Rarity Score:", output)
        self.assertIn("Word: multi |", output)
        self.assertIn("Word: line |", output)

    def generate_text(self, word_count):
        words = ['the', 'quick', 'brown', 'fox', 'jumps', 'over', 'lazy', 'dog']
        return ' '.join(random.choice(words) for _ in range(word_count))

    def test_performance(self):
        sizes = [100, 1000, 10000]
        max_times = [0.1, 1, 10]  # Maximum allowed time in seconds for each size

        for size, max_time in zip(sizes, max_times):
            text = self.generate_text(size)
            
            start_time = time.time()
            results, avg_rarity = analyze_rarity(text)  # Remove max_length parameter
            end_time = time.time()

            execution_time = end_time - start_time
            
            self.assertLess(execution_time, max_time, 
                            f"Performance test failed for {size} words. "
                            f"Time taken: {execution_time:.2f}s, Max allowed: {max_time}s")
            
            print(f"Performance test for {size} words: {execution_time:.2f}s")

    def test_edge_cases(self):
        # Test extremely short words
        self.assertLess(word_rarity('a'), 2, "Single letter common words should have low rarity")
        self.assertLess(word_rarity('the'), 2, "Common words should have low rarity")
        
        # Test extremely long words
        long_word = 'a' * 50
        self.assertEqual(word_rarity(long_word), 8, "Very long words should have maximum rarity")
        
        # Test input with only spaces or newlines
        results, avg_rarity = analyze_rarity("   \n\n   ")
        self.assertEqual(len(results), 0, "Input with only spaces should return no results")
        self.assertEqual(avg_rarity, 0, "Input with only spaces should have zero average rarity")
        
        # Test input with Unicode characters
        unicode_text = "こんにちは world Здравствуй мир"
        results, avg_rarity = analyze_rarity(unicode_text)
        self.assertGreater(len(results), 0, "Unicode text should be analyzed")
        self.assertTrue(any('こんにちは' in word for word, _ in results), "Japanese word should be in results")
        self.assertTrue(any('здравствуй' in word for word, _ in results), "Russian word should be in results")

if __name__ == '__main__':
    unittest.main()