from flask import Flask, request, redirect, url_for
import requests
from sklearn.feature_extraction.text import CountVectorizer



def update_query_vector(query_vector, swipe_direction):

    updated_query_vector = {}

    # Assign weights to each term
    for term in query_vector:
        # Initialize the weight for the term to 1
        updated_query_vector[term] = []

        # Assign weight for each value in the term list
        for value in query_vector[term]:
            updated_query_vector[term].append((value, 1))

    # Update query vector based on swipe direction
    if swipe_direction == 'left':
        # Decrease the weight by swipe_weight for each term
        for term in updated_query_vector:
            for i, (value, weight) in enumerate(updated_query_vector[term]):
                updated_query_vector[term][i] = (value, weight - .5)
        print(updated_query_vector)
    elif swipe_direction == 'right':
    
        # Increase the weight by swipe_weight for each term
        for term in updated_query_vector:
            for i, (value, weight) in enumerate(updated_query_vector[term]):
                updated_query_vector[term][i] = (value, weight + .5)
        print(updated_query_vector)
    print(updated_query_vector)
    return updated_query_vector
   

