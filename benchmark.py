from typing import Dict, List, Tuple
import json
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup


class EpubBenchmark:
    # ------------------------------------------------------------------ #
    # Construction & parsing                                             #
    # ------------------------------------------------------------------ #
    def __init__(self, gt_path: str, test_path: str) -> None:
        self.gt_maps, self.gt_seq = self._parse_epub(gt_path)
        self.test_maps, self.test_seq = self._parse_epub(test_path)

    @staticmethod
    def _parse_epub(
        file_path: str,
    ) -> Tuple[Dict[str, Dict[str, str]], Dict[str, List[str]]]:
        """
        Returns two structures:

        maps[cat][key]   -> speaker               (random order)
        seq[cat]         -> [speaker0, …]         (document order)
        """
        book = epub.read_epub(file_path)
        items = book.get_items_of_type(ebooklib.ITEM_DOCUMENT)

        maps: Dict[str, Dict[str, str]] = {"speech": {}, "thought": {}}
        seq: Dict[str, List[str]] = {"speech": [], "thought": []}

        for item in items:
            soup = BeautifulSoup(
                item.get_body_content().decode("utf-8"), "html.parser"
            )

            for i, tag in enumerate(soup.find_all("speech")):
                speaker = (tag.get("speaker") or "Unknown").strip()
                maps["speech"][f"{item.id}_{i}"] = speaker
                seq["speech"].append(speaker)

            for i, tag in enumerate(soup.find_all("thought")):
                speaker = (tag.get("speaker") or "Unknown").strip()
                maps["thought"][f"{item.id}_{i}"] = speaker
                seq["thought"].append(speaker)

        return maps, seq

    # ------------------------------------------------------------------ #
    # Accuracy helpers                                                   #
    # ------------------------------------------------------------------ #
    def _matches_and_total(self, cat: str) -> Tuple[int, int]:
        """(#matches, total positions) for the given category."""
        gt, test = self.gt_seq[cat], self.test_seq[cat]
        total = max(len(gt), len(test))
        matches = sum(
            1
            for i in range(total)
            if (gt[i] if i < len(gt) else "MISSING").strip().casefold()
            == (test[i] if i < len(test) else "MISSING").strip().casefold()
        )
        return matches, total

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    def generate_report(self) -> Dict[str, float]:
        """Return overall and per-class accuracies."""
        sp_ok, sp_tot = self._matches_and_total("speech")
        th_ok, th_tot = self._matches_and_total("thought")

        total_ok = sp_ok + th_ok
        total_cnt = sp_tot + th_tot

        return {
            "speech_accuracy": sp_ok / sp_tot if sp_tot else 0,
            "thought_accuracy": th_ok / th_tot if th_tot else 0,
            "overall_accuracy": total_ok / total_cnt if total_cnt else 0,
            "gt_speech_count": len(self.gt_seq["speech"]),
            "gt_thought_count": len(self.gt_seq["thought"]),
            "test_speech_count": len(self.test_seq["speech"]),
            "test_thought_count": len(self.test_seq["thought"]),
            "speech_tags_matching": len(self.gt_seq["speech"])
            == len(self.test_seq["speech"]),
            "thought_tags_matching": len(self.gt_seq["thought"])
            == len(self.test_seq["thought"]),
        }

    def compare_tags(
        self, category: str = "speech"
    ) -> List[Dict[str, str | int | bool]]:
        """
        Return **all** tags in order with a match flag.

        Each dict:
            {
              "index"        : int,
              "ground_truth" : str,
              "test_output"  : str,
              "match"        : bool
            }
        """
        gt, test = self.gt_seq[category], self.test_seq[category]
        total = max(len(gt), len(test))
        rows = []

        for i in range(total):
            gt_spk = gt[i] if i < len(gt) else "MISSING"
            test_spk = test[i] if i < len(test) else "MISSING"
            rows.append(
                {
                    "index": i,
                    "ground_truth": gt_spk,
                    "test_output": test_spk,
                    "match": gt_spk.strip().casefold() == test_spk.strip().casefold(),
                }
            )
        return rows

# ---------------------------main----------------------------------- #
if __name__ == "__main__":
    bm = EpubBenchmark("groundtruth-spacehounds.epub", "output.epub")

    print("Report:")
    print(json.dumps(bm.generate_report(), indent=2))

    print("\n Speech tags:")
    print(json.dumps(bm.compare_tags()[:40], indent=2))