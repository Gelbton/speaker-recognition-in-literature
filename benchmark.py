import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from epub_book_parser import EpubParser
from item_chunk import Chunk

class EpubBenchmark:
    def __init__(self, ground_truth_path, test_path):
        self.ground_truth = self._parse_epub(ground_truth_path)
        self.test_output = self._parse_epub(test_path)

    def _parse_epub(self, file_path):
        """Parse EPUB and extract speaker annotations"""
        book = epub.read_epub(file_path)
        parser = EpubParser()
        items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
        
        speakers = {
            'speech': {},
            'thought': {}
        }

        for item in items:
            content = item.get_body_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract speech annotations
            for i, speech in enumerate(soup.find_all('speech')):
                speakers['speech'][f"{item.id}_{i}"] = speech.get('speaker', 'Unknown')
            
            # Extract thought annotations
            for i, thought in enumerate(soup.find_all('em')):
                speakers['thought'][f"{item.id}_{i}"] = thought.get('speaker', 'Unknown')
        
        return speakers

    def _calculate_accuracy(self, category):
        """Calculate accuracy for a specific category (speech/thought)"""
        total = 0
        correct = 0

        for key in self.ground_truth[category]:
            total += 1
            if self.test_output[category].get(key) == self.ground_truth[category][key]:
                correct += 1

        return correct / total if total > 0 else 0

    def generate_report(self):
        """Generate comprehensive accuracy report"""
        return {
            'speech_accuracy': self._calculate_accuracy('speech'),
            'thought_accuracy': self._calculate_accuracy('thought'),
            'overall_accuracy': (
                self._calculate_accuracy('speech') + self._calculate_accuracy('thought')
            ) / 2
        }

    def show_diff(self):
        """Show textual differences between ground truth and output"""
        diffs = {
            'speech': [],
            'thought': []
        }

        for category in ['speech', 'thought']:
            for key in self.ground_truth[category]:
                gt = self.ground_truth[category][key]
                test = self.test_output[category].get(key, 'MISSING')
                if gt != test:
                    diffs[category].append({
                        'position': key,
                        'ground_truth': gt,
                        'test_output': test
                    })
        
        return diffs

if __name__ == "__main__":
    benchmark = EpubBenchmark(
        ground_truth_path="ground_truth.epub",
        test_path="output.epub"
    )
    
    report = benchmark.generate_report()
    print(f"Speech Recognition Accuracy: {report['speech_accuracy']:.2%}")
    print(f"Thought Recognition Accuracy: {report['thought_accuracy']:.2%}")
    print(f"Overall Accuracy: {report['overall_accuracy']:.2%}")
    
    # Uncomment to see detailed differences
    # diff_report = benchmark.show_diff()
    # print("\nDetailed Differences:")
    # print(json.dumps(diff_report, indent=2))