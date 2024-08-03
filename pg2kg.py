import os
import psycopg2
import csv
from pg2kg_queries import *

def fetch_records(query):
    columns = []
    results = []
    with psycopg2.connect(database="aact",
                        host="aact-db.ctti-clinicaltrials.org",
                        user=os.environ.get('AACT_USERNAME'),
                        password=os.environ.get('AACT_PASSWORD'),
                        port="5432") as conn:
     with conn.cursor() as cursor:
       cursor.execute(query)
       # transform results
       columns = list(cursor.description)
       results = cursor.fetchall()
    return results, columns

def convert_to_dict(tuple_records, columns):
    # make dict
    results = []
    for row in tuple_records:
        row_dict = {}
        for i, col in enumerate(columns):
           row_dict[col.name] = row[i]
        results.append(row_dict)
    return results

def convert_to_ttl(results, class_name):
    with open(class_name + ".ttl", "w", encoding='utf-8') as file_handle:
        for row in results:
            rows = []
            for key, value in row.items():
                if str(value) != "None":  # dont use null values
                    if key == 'nct_id': # if primary key
                        instance_id = str(value)
                        rows.append("ctgo:" + instance_id + " a ctgo:" + class_name + " ;\n")
                    else:
                        rows.append("ctgo:" + key + " \"" + str(value) + "\" ;\n")
            rows[-1] = rows[-1].replace(";\n", ".\n")
            file_handle.writelines(rows)

def convert_to_CSV(results, class_name):
    with open(class_name + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for row in results:
            for key, value in row.items():
                if str(value) != "None":  # dont use null values
                    if key == 'name':
                        int_name = str(value)
                    if key == 'intervention_type':
                        if row['intervention_type'] == 'Other':
                            int_type = str(value + '-Intervention')
                        else:
                            int_type = str(value)
                    else:
                        break
            writer.writerow([int_name,"is_a",int_type])
            
            #        if key == 'nct_id': # if primary key
            #            instance_id = str(value)
            #            writer.writerow([instance_id, "is_a", class_name])
            #        elif key == 'instance_id':
            #            instance_id = str(value)
            #        else:
            #            writer.writerow([instance_id, key, str(value)])
            #            if key == 'studies_condition':
            #                writer.writerow([str(value),"is_studied_in",instance_id])

###################################################################
queries()
print(intv_inst_query)
queries = [intv_inst_query]
#dict_list = []
for query in queries:
    break
    results, columns = fetch_records(query)
    if results != []:
        print("fetched records")
        dict_results = convert_to_dict(results, columns)
        print("converted results to dict")
        class_name = input("Enter class name: ")
        convert_to_CSV(dict_results, class_name)
        #for dict in dict_results:
        #    dict_list.append(dict)
    else:
        print("no results for the query given")


