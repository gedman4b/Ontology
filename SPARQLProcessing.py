import json
from flask_restful import Resource, reqparse
import spacy
from spacy.matcher import Matcher
import nltk
from owlready2 import *
from re import sub
import warnings
warnings.filterwarnings("ignore")

prefix_header = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX mcto: <http://www.mraas.ai/ontologies/mcto#>

"""

def get_entities_chunks(tokens):
    chunk_list = []
    for chunk in tokens.noun_chunks:
        chunk_list.append(chunk.text)

    end_list = []
    for ent in tokens.ents:
        if ent.text not in chunk_list:
            ent_list.append(ent.text)
    return (chunk_list + ent_list)

def get_entities(tokens):
    ent_list = []
    for ent in tokens.ents:
        ent_list.append(ent.text)

    return ent_list

def get_relations(matcher, token):
    # create pattern matching predicates
    # , {'POS':'ADP', 'OP':'?'}
    # {'POS':{'IN': ['is','are','am','was','were','have','has','had','will','be'}],
    patterns = [
        [{'POS':'AUX', 'OP':'?'}, {'POS':'VERB'}, {'POS':'ADP', 'OP':'?'}],
        [{'POS':'NOUN'},{'POS':'ADP'}]
    ]
    # Add the pattern to the matcher
    matcher.add("RELATION_PATTERN", patterns, greedy="LONGEST")

    # Use the matcher on the doc
    matches = matcher(tokens)

    matches_list = [tokens[start:end].text for match_id, start, end in matches]
    for match in matches_list:
        if match.lower() in ['are','am','have','was','were','had','will','be']:
            matches_list.remove(match)
        else:
            pass
            # TODO if AUX VERB is detected as matched pattern then Camel case the 2 words and remove on of the words from the matches_list
    return matches_list

def convert_TitleCase(s):
    if s[-1] == 's':
        s = stitle().replace(" ","").rstrip(s[-1])
    else:
        s = s.title().replace(" ", "")
    return s

def convert_camelCase(s):
    s = sub(r"(_|-)+", " ", s).title().replace(" ", "")
    s = ''.join([s[0].lower(), s[1:]])
    return s

nlp = spacy.load('en_core_sci_lg')

class NLP(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('search', required=True)
        args = parser.parse_args()

        # Initialize the Matcher with the shared vocabulary
        # r_matcher = Matcher(nlp.vocab)

        words = nltk.word_tokenize(args['search'])
        #removes punctuation
        sentence = ' '.join([word for word in words  if word.isalnum()])
        tokens = nlp(sentence)

        entities = get_entities(token)
        # relations = get_relations(r_matcher, tokens)
        if entities != []:
            for e in entities:
                for r in relations:
                    if e in r:
                        entities.remove(e)
                        # entities : ["High volume disease","presence","visceral metastases",
                        #"bone metastases", "verterbral bodies", "pelvis"]
                        # relations : ["defined","presence of","metastases with"]
            return {"entities": json.dumps(entities)}, 200
        else:
            return {"entities": json.dumps('No entities')}, 200
            # , "relations": json.dumps('No relations')
onto = get_ontology("ctgo.owl").load()
graph = default_world.as_rdflib_graph()

class TripleQuery(Resource):
    # Tries to see if a specific triple <e1,r, e2> exists
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('e1', required=True)
        parser.add_argument('r', required=True)
        parser.add_argument('e2', required-True)
        args = parser.parse_args() # parse arguments to dictionary

        e1 = convert_TitleCase(args['e1'])
        e2 = convert_TitleCase(args['e2'])
        r = convert_camelCase(args['r'])

        eng = "@en"
        query = "ASK { mcto:" + r + " rdfs:domain mcto:" + e1 + " ; rdfs:range mcto:" + e2 + " . }"

        q_string =  prefix_header + query
        print(query)
        qres = graph.query(q_string) # returns a SPARQL Result

        for row in qres:
            res = []
            if isinstance(row, bool):
                return {'data': row}, 200
            else:
                res.append(graph.label(row.object))
                return {'data': json.dumps(res)}, 200
            return {'data': json.dump('No results')}, 200

class PredicateQuery(Resource):
    # Tries to find a relationship between 2 entities
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('e1', required=True)
        parser.add_argument('e2', required-True)
        args = parser.parse_args() # parse arguments to dictionary

        e1 = convert_TitleCase(args['e1'])
        e2 = convert_TitleCase(args['e2'])

        query = "SELECT DISTINCT ?rlabel WHERE { ?r rdfs:domain mcto:" + e1 + " ; rdfs:range mcto:" + e2 + " ; rdfs:label ?rlabel . }"
        q_string =  prefix_header + query
        print(query)
        qres = graph.query(q_string) # returns a SPARQL Result

        for row in qres:
            if row != 'null\n':
                return {'data': row}, 200
            else:
                return {'data': 'No Results'}, 200

class IndividualQuery(Resource):
    # Tries to find all individuals for an entity
    def get(self):
        parser.add_argument('e1', required=True)
        parser.add_argument('r1', required-True)
        args = parser.parse_args() # parse arguments to dictionary

        e1 = convert_TitleCase(args['e1'])
        r1 = convert_camelCase(args['r1'])
        query = "SELECT DISTINCT ?indiv ?o WHERE {?indiv a mcto:" + e1 + " ; mcto:" + r1 + " ?o . } ORDER BY ?indiv"
        q_string =  prefix_header + query
        print(query)
        qres = graph.query(q_string) # returns a SPARQL Result

        results = []
        for row in qres:
            if row != []:
                results.append(graph.label(row[0]))
            else:
                return {'data': json.dumps('No results')}, 200
            print(results)
        return {'data': json.dumps(results)}, 200

class IndividualInference(Resource):
    # Tries to find all individuals for an entity
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('e1', required=True)
        parser.add_argument('r1', required=True)
        parser.add_argument('e2', required-True)
        args = parser.parse_args() # parse arguments to dictionary

        e1 = convert_TitleCase(args['e1'])
        e2 = convert_TitleCase(args['e2'])
        r = convert_camelCase(args['r1'])

        query = "CONSTRUCT { mcto:" + e2 + " mcto:produces ?indiv1 } WHERE { ?indiv1 a mcto:" + e1 + " . ?indiv2 a mcto:" + e2 + " . ?indiv2 mcto:produces ?indiv1 . }"
        q_string =  prefix_header + query
        #print(query)
        qres = graph.query(q_string) # returns a SPARQL Result

        results = []
        for row in qres:
            if row != []:
                dict = {}
                dict['entity1'] = graph.label(row[0])
                dict['relation'] = graph.label(row[1])
                dict['entity2'] = graph.label(row[2])
                results.append(dict)
                #print(graph.label(row))
            else:
                return {'data': json.dumps('No results')}, 200
        print(results)
        return {'data': json.dumps(results)}, 200
