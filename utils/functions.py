import pandas as pd
from utils.sparql_queries import find_node_with_description, forward_backward
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Keyword search
def get_node(keyword, sparql, JSON):
    sparql.setQuery(find_node_with_description.format(keyword))
    sparql.setReturnFormat(JSON)
    query_results_list = sparql.query().convert()

    data = []
    for result in query_results_list["results"]["bindings"]:
        node_value = result['node']['value']
        description_value = result['schemaDescription']['value']
        label_value = result['nodeLabel']['value']
        data.append([node_value, label_value, description_value])

    # dataframe to store the results
    df_query_results = pd.DataFrame(data, columns=["node", "nodeLabel", "description"])
    df_query_results = df_query_results.drop_duplicates()
    
    return df_query_results


# Generate a subgraph
def get_subgraph(item: str, goal_name: str, model_sts, sparql, JSON, depth: int):
    visited = set()  # To keep track of visited nodes to avoid revisiting them
    queue = [(item, 1)]  # Using a queue for BFS traversal
    data = []

    while queue:
        print("queue: " + str(queue))
        current_item, current_depth = queue.pop(0)  # Dequeuing the node for exploration

        print("\n")
        print('current_item: ' + str(current_item))

        print("\n")
        print('current_depth: ' + str(current_depth))


        # The traversal stops when the specified depth limit is reached
        if current_depth > depth:
            break

        # Skip already visited nodes
        if current_item in visited:
            continue 

        visited.add(current_item)

        print("\n")
        print(visited)

        # Query neighbors of the current item
        sparql.setQuery(forward_backward.format(current_item))
        sparql.setReturnFormat(JSON)
        query_results = sparql.query().convert()

        # Extract triples and add neighbors to the queue
        for row in query_results["results"]["bindings"]:
            subject_id = row['subject']['value']
            predicate_id = row['predicate']['value']
            object_id = row['object']['value']
            triple_labelized = f"{row['subject_label']['value']} {row['predicate_label']['value']} {row['object_label']['value']}"

            # Add triple to data
            data.append({'TRIPLE_LABELIZED': triple_labelized, 'SUBJECT_ID': subject_id, 'PREDICATE_ID': predicate_id, 'OBJECT_ID': object_id, 'GOAL': goal_name})

            # Add neighbors to the queue
            if subject_id not in visited:
                queue.append((subject_id, current_depth + 1))

            if object_id not in visited:
                queue.append((object_id, current_depth + 1))


        goal_triples_df = pd.DataFrame(data)

        print("\n")
        print("DATA:")

        print("\n")
        print(goal_triples_df.to_string())

        print("\n")
        print(len(goal_triples_df))

        goal_triples_df.to_csv("data.csv", index=False)

        # calculate the cosine similarity between triples and goal
        goal_triples_df['SIMILARITY_SCORE'] = goal_triples_df.apply(
            lambda row: pd.Series(
                cosine_similarity(
                    model_sts.encode(row['GOAL']).reshape(1, -1),  # goal embedding
                    model_sts.encode(row['TRIPLE_LABELIZED']).reshape(1, -1),  # simple triples embedding
                ) .flatten()
            ),
            axis=1
        )
        goal_triples_df.sort_values(by=['SIMILARITY_SCORE'], inplace=True, ascending=False)

        highest_score = goal_triples_df['SIMILARITY_SCORE'].max()
        highest_score_triples = goal_triples_df[goal_triples_df['SIMILARITY_SCORE'] >= highest_score * 0.85]    

        print("\nHighest scoring triples:")
        print(highest_score_triples.to_string())

        print("\nLength highest scoring triples:")
        print(len(highest_score_triples.index))

        # Update the queue with the relevant nodes for next iteration
        #for idx, row in highest_score_triples.iterrows():
        #    subj = row['SUBJECT_ID']
        #    obj = row['OBJECT_ID']

            # Add neighbors to the queue
        #    if subj not in visited:
        #        queue.append((subj, current_depth + 1))

        #    if obj not in visited:
        #        queue.append((obj, current_depth + 1))

    # CSV files is generated to store the results
    highest_score_triples.to_csv("subgraph_with_depth_"+str(depth)+".csv", index=False) 
    
    return highest_score_triples



def traverse_graph(item, model_sts, sparql, JSON, depth, visited=None):
    if visited is None:
        visited = set()

    if depth == 0 or item in visited:
        return []

    visited.add(item)

    # Query neighbors of the current item
    sparql.setQuery(forward_backward.format(item))
    sparql.setReturnFormat(JSON)
    query_results = sparql.query().convert()

    triples = []
    for row in query_results["results"]["bindings"]:
        subject_id = row['subject']['value']
        predicate_id = row['predicate']['value']
        object_id = row['object']['value']
        triple_labelized = f"{row['subject_label']['value']} {row['predicate_label']['value']} {row['object_label']['value']}"

        # Add triple to list
        triples.append((triple_labelized, subject_id, predicate_id, object_id))

        # Traverse neighbors recursively
        if depth > 1:
            for neighbor_id in [subject_id, object_id]:
                if neighbor_id not in visited:
                    triples += traverse_graph(neighbor_id, model_sts, sparql, JSON, depth - 1, visited)

    return triples


def get_subgraph_v2(item: str, goal_name: str, model_sts, sparql, JSON, depth: int):
    visited = set()  # To keep track of visited nodes to avoid revisiting them

    # Traverse the graph from the input item
    triples = traverse_graph(item, model_sts, sparql, JSON, depth, visited)

    # Create DataFrame from collected triples
    data = [{'TRIPLE_LABELIZED': t[0], 'SUBJECT_ID': t[1], 'PREDICATE_ID': t[2], 'OBJECT_ID': t[3], 'GOAL': goal_name}
            for t in triples]
    goal_triples_df = pd.DataFrame(data)

    # Calculate similarity scores
    goal_triples_df['SIMILARITY_SCORE'] = goal_triples_df.apply(
        lambda row: pd.Series(
            cosine_similarity(
                model_sts.encode(row['GOAL']).reshape(1, -1),  # goal embedding
                model_sts.encode(row['TRIPLE_LABELIZED']).reshape(1, -1),  # simple triples embedding
            ).flatten()
        ),
        axis=1
    )
    goal_triples_df.sort_values(by=['SIMILARITY_SCORE'], inplace=True, ascending=False)

    # Save results to CSV
    goal_triples_df.to_csv("subgraph_with_depth_" + str(depth) + ".csv", index=False)

    return goal_triples_df
