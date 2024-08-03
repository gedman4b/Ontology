import json
import requests
import warnings
warnings.filterwarnings("ignore")

def get_nlp_results(endpoint_url, search_text):
    response = requests.get(endpoint_url, params={'search': search_text}, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def get_triples_results(endpoint_url, entity1, relation, entity2):
    response = requests.get(endpoint_url, params={'e1': entity1, 'r': relation, 'e2': entity2}, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def get_predicate_results(endpoint_url, entity1, entity2):
    response = requests.get(endpoint_url, params={'e1': entity1, 'e2': entity2}, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def get_individuals_results(endpoint_url, entity1, relation):
    response = requests.get(endpoint_url, params={'e1': entity1, 'r1': relation}, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def get_inference_results(endpoint_url, entity1, relation, entity2):
    response = requests.get(endpoint_url, params={'e1': entity1, 'r1': relation, 'e2': entity2}, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

service = "http://localhost:5000"

def start_nlp_client(search_text):
    endpoint_url = service + "/nlpservice"
    results = json.loads(get_nlp_results(endpoint_url, search_text))
    return results

def start_triples_client(entity1, relation, entity2):
    endpoint_url = service + "/checktriples"
    results = json.loads(get_triples_results(endpoint_url, entity1, relation, entity2))
    return results

def start_predicate_client(entity1, entity2):
    endpoint_url = service + "/checkpredicate"
    results = json.loads(get_predicate_results(endpoint_url, entity1, entity2))
    return results

def start_individuals_client(entity, relation):
    endpoint_url = service + "/checkindividuals"
    results = json.loads(get_individuals_results(endpoint_url, entity1, relation, entity2))
    return results

def start_inference_client(entity1, relation, entity2):
    endpoint_url = service + "/inferindividuals"
    results = json.loads(get_inference_results(endpoint_url, entity1, relation, entity2))
    return results
