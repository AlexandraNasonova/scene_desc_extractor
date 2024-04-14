import os
import re
import scene_desc as sd


class ConlluFilesConverter:
    TEXT_MARKER = "# text = "
    SENTENCE_ID_MARKER = "# sent_id = "
    TEXT_MARKER_LEN = len(TEXT_MARKER)
    ENTITY_START_MARKER = "Entity="
    ENTITY_STOP_MARKER = "|"
    ENTITY_MARKER_LEN = len(ENTITY_START_MARKER)

    def __init__(self, max_level=5, cls_tag='[CLS]', sep_tag='[SEP]', begin_entity_tag='B',
                 inside_entity_tag='I', last_entity_tag='L', outside_entity_tag='O', unique_entity_tag='U'):
        self.max_level = max_level
        self.cls_tag = cls_tag
        self.sep_tag = sep_tag
        self.begin_entity_tag = begin_entity_tag
        self.inside_entity_tag = inside_entity_tag
        self.last_entity_tag = last_entity_tag
        self.outside_entity_tag = outside_entity_tag
        self.unique_entity_tag = unique_entity_tag

    def __extract_entity_info(self, text: str) -> (str, list[(str, str)]):
        entity_start_mark_index = text.find(self.ENTITY_START_MARKER)
        if entity_start_mark_index == -1:
            return '_', []

        entity_stop_mark_index = text.find(self.ENTITY_STOP_MARKER)
        if entity_stop_mark_index > entity_start_mark_index:
            entity_tag = text[entity_start_mark_index + self.ENTITY_MARKER_LEN:entity_stop_mark_index]
        else:
            entity_tag = text[entity_start_mark_index + self.ENTITY_MARKER_LEN:]
        entity_matches = re.findall(r'(\(\d+-\w+)(?=-|\:)|(\d*?\))', entity_tag)

        return entity_tag, entity_matches

    def __append_open_entities_as_inside(self, word_id: int, open_entities: list[sd.Entity],
                                         result_entities=list[sd.Entity]) -> None:
        for entity in open_entities:
            if entity.word_id == word_id:
                continue
            entity = sd.Entity(word_id=word_id, coref_id=entity.coref_id,
                               bilou_tag=self.inside_entity_tag, level=entity.level)
            result_entities.insert(entity.level, entity)

    def __parse_entity_matches(self, word_id: int, entity_matches: list[(str, str)],
                               coref_entities: dict[int, str],
                               open_entities: list[sd.Entity]) -> list[sd.Entity]:
        result_entities = []
        # if no openings or closings or already opened entities return tag O (Outside)
        if len(entity_matches) == 0 and len(open_entities) == 0:
            return [sd.Entity(word_id=word_id, coref_id=0, bilou_tag=self.outside_entity_tag, level=0)]

        # if there are some openings or closings for entities
        for match in entity_matches:
            entity_start, entity_end = match[0], match[1]

            # for an opening
            if entity_start != '':
                spl = entity_start[1:].split('-')
                (coref_id, entity_type) = int(spl[0]), spl[1]
                # get new level
                level = 0 if len(open_entities) == 0 else open_entities[-1].level + 1
                # all levels deeper than max_level should be ignored
                if level <= self.max_level:
                    # if opening is newly mentioned, update coreference dictionary
                    if coref_id not in coref_entities:
                        coref_entities[coref_id] = entity_type
                    # create a new entity with B - Begin BILOU tag as default
                    entity = sd.Entity(word_id=word_id, coref_id=coref_id, bilou_tag=self.begin_entity_tag, level=level)
                    open_entities.append(entity)
                    result_entities.append(entity)

            # for a closing
            elif len(open_entities) > 0:
                spl = entity_end[:-1]
                # if not links to coref_if then the last opening should be tagged U (Unique) if its level is not ignored
                if spl == '':
                    if len(result_entities) > 0:
                        result_entities[-1].bilou_tag = self.unique_entity_tag
                        open_entities.pop()

                # if there is the link to coref_if, then tag L (Last) should be used
                else:
                    coref_id = int(spl)
                    open_entity_index = -100
                    for i, o in enumerate(open_entities):
                        if o.coref_id == coref_id:
                            open_entity_index = i
                            break
                    if open_entity_index >= 0:
                        entity = sd.Entity(word_id=word_id, coref_id=coref_id, bilou_tag=self.last_entity_tag,
                                           level=open_entities[open_entity_index].level)
                        result_entities.insert(open_entities[open_entity_index].level, entity)
                        open_entities.pop(open_entity_index)

        # update already opened entities with nested info
        self.__append_open_entities_as_inside(word_id=word_id, open_entities=open_entities,
                                              result_entities=result_entities)
        return result_entities

    def __parse_conllu_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

            text = sd.Text(text_full="", sentences=[], coref_entities={})
            open_entities = []
            sentence_text = ''
            sentence = None
            # Iterate through each line in the file
            for line in lines:
                # collect text
                if line.startswith(self.TEXT_MARKER):
                    sentence_text = line[self.TEXT_MARKER_LEN:-1]
                    text.text_full += sentence_text + " "

                # init new sentence
                if line.startswith(self.SENTENCE_ID_MARKER):
                    if sentence is not None:
                        text.sentences.append(sentence)
                    sentence_id = int(line[(line.rfind('-') + 1):])
                    sentence = sd.Sentence(sentence_id=sentence_id, sentence_text=sentence_text,
                                           words=[])

                # collect line info for words and punctuation
                if line[0].isdigit():
                    parts = line.split("\t")
                    word_id = parts[0]
                    entity_tag, entity_matches = self.__extract_entity_info(text=parts[9])
                    # get BILOU entities for each words
                    entities = self.__parse_entity_matches(word_id=word_id,
                                                           entity_matches=entity_matches,
                                                           coref_entities=text.coref_entities,
                                                           open_entities=open_entities)
                    # collect word info
                    word = sd.Word(word_id=word_id, word=parts[1], lemma_init=parts[2],
                                   pos_tag=parts[3], dep_type=parts[7], dep_parent_id=parts[6],
                                   entities=entities)

                    # print(f'{sentence_id}_{word_id}\t{parts[1]}\t{entity_tag}\n'
                    #       f'\t\t[{" | ".join("(" + str(e) + ")" for e in entities)}]\n'
                    #       f'\t\t[{" | ".join("(" + str(e) + ")" for e in open_entities)}]'
                    #       )

                    # append word to current sentence
                    sentence.words.append(word)

            if sentence is not None:
                text.sentences.append(sentence)
            text.text_full = text.text_full.strip()
            return text

    def __parsed_text_to_labels_str(self, text: sd.Text):
        lines = []

        for sentence in text.sentences:
            sentence_id = sentence.sentence_id

            # append [CLS] Tag
            if self.cls_tag is not None and self.cls_tag != '':
                line = sd.LabelLine(sentence_id=sentence_id,
                                    word=sd.Word(word_id=0, word=self.cls_tag, lemma_init=self.cls_tag,
                                                 pos_tag='_', dep_type='_', dep_parent_id=-1, entities=None),
                                    max_level=self.max_level)
                lines.append(str(line))

            # append words lines
            for word in sentence.words:
                line = sd.LabelLine(sentence_id=sentence_id, word=word, max_level=self.max_level)
                for entity in word.entities:
                    if entity.bilou_tag == self.outside_entity_tag:
                        line.entities.append((-1, self.outside_entity_tag))
                    else:
                        bilou_tag = entity.bilou_tag + '-' + text.coref_entities[entity.coref_id]
                        line.entities.append((entity.coref_id, bilou_tag))
                lines.append(str(line))

            # append [CLS] Tag
            if self.sep_tag is not None and self.sep_tag != '':
                line = sd.LabelLine(sentence_id=sentence_id,
                                    word=sd.Word(word_id=len(sentence.words) + 1,
                                                 word=self.sep_tag, lemma_init=self.sep_tag, pos_tag='_',
                                                 dep_type='_', dep_parent_id=-1, entities=None),
                                    max_level=self.max_level)
                lines.append(str(line))

        return '\n'.join(lines)

    @staticmethod
    def __coref_dict_to_str(text: sd.Text):
        return '\n'.join([f'{key}\t{val}' for key, val in text.coref_entities.items()])

    def convert_and_save_folder(self, source_folder: str, target_folder: str) -> None:
        source_file_names = os.listdir(source_folder)
        source_file_paths = [os.path.join(source_folder, file_name) for file_name in source_file_names]
        for i, source_file_path in enumerate(source_file_paths):
            target_file_path = os.path.join(target_folder, f'{str(i)}.txt')
            self.convert_and_save_file(source_file_path, target_file_path)

    def convert_and_save_file(self, source_file_path: str,
                              target_text_file_path: str,
                              coref_dict_file_path: str,
                              target_labels_file_path: str) -> None:
        parsed_text = self.__parse_conllu_file(source_file_path)
        corefs_dict_str = self.__coref_dict_to_str(parsed_text)
        labels_str = self.__parsed_text_to_labels_str(parsed_text)
        with open(target_text_file_path, 'w') as file:
            file.write(parsed_text.text_full)
        with open(coref_dict_file_path, 'w') as file:
            file.write(corefs_dict_str)
        with open(target_labels_file_path, 'w') as file:
            file.write(labels_str)
