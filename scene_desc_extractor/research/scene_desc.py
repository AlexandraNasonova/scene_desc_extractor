import numpy as np


class Entity:
    def __init__(self, word_id: int, coref_id: int,
                 bilou_tag, level: int):
        self.coref_id = coref_id
        self.bilou_tag = bilou_tag
        self.level = level
        self.word_id = word_id

    def __str__(self):
        return (f'level: {self.level}, coref_id: {self.coref_id}, '
                f'bilou_tag: {self.bilou_tag}')


class Word:
    def __init__(self, word_id: int, word: str, lemma_init: str,
                 pos_tag: str, dep_type: str, dep_parent_id: int,
                 entities: list[Entity]):
        self.word_id = word_id
        self.word = word
        self.lemma_init = lemma_init
        self.pos_tag = pos_tag
        self.dep_type = dep_type
        self.dep_parent_id = dep_parent_id
        self.entities = entities

    def __str__(self):
        return (f'word_id : {self.word_id}, word: {self.word}, '
                f'lemma_init: {self.lemma_init}, pos_tag: {self.pos_tag}, '
                f'dep_type: {self.dep_type}, dep_parent_id: {self.dep_parent_id}, '
                f'\nentities: {[{" | ".join("(" + str(e) + ")" for e in self.entities)}]})')


class Sentence:
    def __init__(self, sentence_id: int, sentence_text: str, words: list[Word]):
        self.sentence_id = sentence_id
        self.sentence_text = sentence_text
        self.words = words


class Text:

    def __init__(self, text_full: str, sentences: list[Sentence], coref_entities: list[str]):
        self.text_full = text_full
        self.sentences = sentences
        self.coref_entities = coref_entities
#
#     def prepare_labels(self):
#         result = ''
#         result = '\n'.join(
#             '\t'.join([s for s in self.sentences]






# class Entity:
#     def __init__(self, entity_type: str, entity_id: int, parent_entity_id: int,
#                  first_lemma: Lemma):
#         self.entity_type = entity_type
#         self.entity_id = entity_id
#         self.parent_entity_id = parent_entity_id
#         self.mentions = [[first_lemma]]
#         self.children_entity_ids = []
#
#     def add_child(self, child_entity_id: int):
#         self.children_entity_ids.append(child_entity_id)
#
#     def add_lemma(self, lemma: Lemma, new_mention: bool):
#         if new_mention:
#             self.mentions.append([lemma])
#         else:
#             self.mentions[-1].append(lemma)
#
#
# class SceneDesc:
#
#     def __init__(self):
#         self.entities: list[Entity] = []
#
#     def add_entity(self, entity: Entity):
#         self.entities.append(entity)
#
#     def get_most_frequent_entities(self, selected_entities: list[Entity], frequencies: list[int],
#                                    threshold_coefficient=2) -> list[Entity]:
#         mean, std = np.mean(frequencies), np.std(frequencies)
#         frequent_entities = [selected_entities[i] for i, freq
#                              in enumerate(frequencies)
#                              if freq > (mean + threshold_coefficient * std)]
#         return frequent_entities
#
#     def get_main_characters(self):
#         characters = [e for e in self.entities if e.entity_type in ('person', 'object', 'animal', 'plant')]
#         mentions_counts = [len(c.mentions) for c in characters]
#         lemmas_counts = [len(m) for m in [c.mentions for c in characters]]
#         refs_counts = [len(c.children_entity_ids) for c in characters]
#         freq_mentions = self.get_most_frequent_entities(characters, mentions_counts)
#         freq_lemmas = self.get_most_frequent_entities(characters, lemmas_counts)
#         freq_refs = self.get_most_frequent_entities(characters, refs_counts)
#
#         return freq_mentions + freq_lemmas + freq_refs
#
#     def get_second_characters(self):
#         pass
#
#     def background(self):
#         pass

