__author__ = 'wenqihe'

import json
import sys
from corenlp import StanfordCoreNLP


class NLPParser(object):
    """
    NLP parse, including Part-Of-Speech tagging and dependency parse.
    Attributes
    ==========
    parser: StanfordCoreNLP
        the Staford Core NLP parser
    """
    def __init__(self, corenlp_dir):
        self.parser = StanfordCoreNLP(corenlp_dir)

    def parse(self, sent):
        """
        Part-Of-Speech tagging and dependency parse.
        :param sent: string
        :return: a list of tuple (word, pos, dependency)
        """
        result = self.parser.raw_parse(sent)
        tuples = []
        for s in result['sentences']:
            word, pos, dependency = [], [], []
            for dep in s['dependencies']:
                dependency.append({'type': dep[0], 'dep': int(dep[2])-1, 'gov': int(dep[4])-1})
            for w in s['words']:
                word.append(w[0])
                pos.append(w[1]['PartOfSpeech'])
            tuples.append((word, pos, dependency))
        return tuples

def parse(filename, output):
    with open(filename) as f, open(output, 'w') as g:
        parser = NLPParser('DataProcessor/stanford-corenlp-python/corenlp/stanford-corenlp-full-2015-04-20')
        count=0
        for line in f:
            sent = json.loads(line.strip('\r\n'))
            tokens = sent['tokens']
            tuples = parser.parse(' '.join(tokens))
            if len(tuples) == 1 and tuples[0][0] == tokens:
                sent['pos'] = tuples[0][1]
                sent['dep'] = tuples[0][2]
                g.write(json.dumps(sent)+'\n')
            else:
                new_tokens = tuples[0][0]
                new_pos = tuples[0][1]
                new_dep = tuples[0][2]
                for i in xrange(1, len(tuples)):
                    new_tokens.extend(tuples[i][0])
                    new_pos.extend(tuples[i][1])
                    new_dep.extend(tuples[i][2])
                mentions = []
                for m in sent['mentions']:
                    mention = tokens[m['start']:m['end']]
                    if len(mention) ==0:
                        count+=1
                        continue
                    index1, index2 = find_index(new_tokens, mention)
                    if index1 != -1 and index2 != -1:
                        mentions.append({'start':index1, 'end':index2, 'labels':m['labels']})
                sent['tokens'] = new_tokens
                sent['pos'] = new_pos
                sent['dep'] = new_dep
                sent['mentions'] = mentions
                g.write(json.dumps(sent)+'\n')


def find_index(sen_split, word_split):
    index1 = -1
    index2 = -1
    for i in range(len(sen_split)):
        if str(sen_split[i]) == str(word_split[0]):
            flag = True
            k = i
            for j in range(len(word_split)):
                if word_split[j] != sen_split[k]:
                    flag = False
                if k < len(sen_split) - 1:
                    k+=1
            if flag:
                index1 = i
                index2 = i + len(word_split)
    return index1, index2

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: nlp_parse.py -INPUT -OUTPUT')
        exit(1)
    parse(sys.argv[1], sys.argv[2])
