import numpy as np


class Lemma:
    def __init__(self, sentence_id: int, lemma_id: int, lemma: str, lemma_init: str,
                 pos_tag: str, dep_type: str, dep_parent_id: int):
        self.sentence_id = sentence_id
        self.lemma_id = lemma_id
        self.lemma = lemma
        self.lemma_init = lemma_init
        self.pos_tag = pos_tag
        self.dep_type = dep_type
        self.dep_parent_id = dep_parent_id


class Entity:
    def __init__(self, entity_type: str, entity_id: int, parent_entity_id: int,
                 first_lemma: Lemma):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.parent_entity_id = parent_entity_id
        self.mentions = [[first_lemma]]
        self.children_entity_ids = []

    def add_child(self, child_entity_id: int):
        self.children_entity_ids.append(child_entity_id)

    def add_lemma(self, lemma: Lemma, new_mention: bool):
        if new_mention:
            self.mentions.append([lemma])
        else:
            self.mentions[-1].append(lemma)


class SceneDesc:

    def __init__(self):
        self.entities: list[Entity] = []

    def add_entity(self, entity: Entity):
        self.entities.append(entity)

    def get_most_frequent_entities(self, selected_entities: list[Entity], frequencies: list[int],
                                   threshold_coefficient=2) -> list[Entity]:
        mean, std = np.mean(frequencies), np.std(frequencies)
        frequent_entities = [selected_entities[i] for i, freq
                             in enumerate(frequencies)
                             if freq > (mean + threshold_coefficient * std)]
        return frequent_entities

    def get_main_characters(self):
        characters = [e for e in self.entities if e.entity_type in ('person', 'object', 'animal', 'plant')]
        mentions_counts = [len(c.mentions) for c in characters]
        lemmas_counts = [len(m) for m in [c.mentions for c in characters]]
        refs_counts = [len(c.children_entity_ids) for c in characters]
        freq_mentions = self.get_most_frequent_entities(characters, mentions_counts)
        freq_lemmas = self.get_most_frequent_entities(characters, lemmas_counts)
        freq_refs = self.get_most_frequent_entities(characters, refs_counts)

        return freq_mentions + freq_lemmas + freq_refs

    def get_second_characters(self):
        pass

    def background(self):
        pass

