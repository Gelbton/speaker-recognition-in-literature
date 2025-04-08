
class AllSpeakers:
    all_speakers = set()

    @staticmethod
    def enrich_speaker_set(speakers):
        AllSpeakers.all_speakers.update(speakers)
        print(AllSpeakers.all_speakers)