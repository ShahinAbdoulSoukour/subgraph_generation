#####################################
#          Dynamic queries          #
#####################################

# keyword search --> returns the ID, the label and the description
find_node_with_description = """
SELECT DISTINCT ?node ?nodeLabel ?schemaDescription 
WHERE {{
    ?node rdfs:label "{0}"@en.
    OPTIONAL {{ ?node schema:description ?schemaDescription. }}
    FILTER (langMatches( lang(?schemaDescription), "EN" ) )
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""

forward = """
SELECT ?subject_label ?wd_label ?object_label
WHERE 
{{
<{0}> ?wdt ?object .
?wd wikibase:directClaim ?wdt .

# Retrieves the label of the property
?wd rdfs:label ?wd_label . 

<{0}> rdfs:label ?subject_label .

# Retrieves the label of the object.
?object rdfs:label ?object_label .

# Ensures the object and the subject label are in English
FILTER (lang(?object_label) = "en" && lang(?subject_label) = "en") 

# Exclude entities related to the predicate "on focus list of Wikimedia project" (wdt:P5008)
FILTER NOT EXISTS {{ <{0}> wdt:P5008 ?object }} 

# Exclude entities related to the predicate "topic's main category" (wdt:P910)
FILTER NOT EXISTS {{ <{0}> wdt:P910 ?object }} 

# Exclude entities related to the predicate "described by source" (wdt:P1343)
FILTER NOT EXISTS {{ <{0}> wdt:P1343 ?object }}

# Exclude entities related to the predicate "topic's main template" (wdt:P1424)
FILTER NOT EXISTS {{ <{0}> wdt:P1424 ?object }} 

# Exclude entities related to the predicate "different from" (wdt:P1889)
FILTER NOT EXISTS {{ <{0}> wdt:P1889 ?object }} 

FILTER (lang(?wd_label) = "en")

# Requests label translations for the entities in English
SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""



forward_backward_with_filters = """
SELECT ?subject ?subject_label ?predicate ?predicate_label ?object ?object_label
WHERE {{
  {{
    BIND(<{0}> AS ?subject) .

    <{0}> ?predicate ?object .
        
    ?object rdfs:label ?object_label .
    ?wd wikibase:directClaim ?predicate .
    ?wd rdfs:label ?predicate_label .
    
    FILTER (LANG(?object_label) = "en" && LANG(?predicate_label) = "en")
    
    <{0}> rdfs:label ?subject_label .
    FILTER (LANG(?subject_label) = "en")
    
    # Exclude entities related to the predicate "on focus list of Wikimedia project" (wdt:P5008)
    FILTER NOT EXISTS {{ <{0}> wdt:P5008 ?object }} 

    # Exclude entities related to the predicate "described by source" (wdt:P1343)
    FILTER NOT EXISTS {{ <{0}> wdt:P1343 ?object }}
  }}
  UNION
  {{
    BIND(<{0}> AS ?object) .

    ?subject ?predicate <{0}> .
        
    ?subject rdfs:label ?subject_label .
    ?wd wikibase:directClaim ?predicate .
    ?wd rdfs:label ?predicate_label .
    
    FILTER (LANG(?subject_label) = "en" && LANG(?predicate_label) = "en") 
    
    <{0}> rdfs:label ?object_label .
    FILTER (LANG(?object_label) = "en")
    
    # Exclude entities related to significant event "category combines topics" (wdt:P971)
    FILTER NOT EXISTS {{ ?subject wdt:P971 <{0}> . }} 

    # Exclude entities related to the predicate "follows" (wdt:P155)
    FILTER NOT EXISTS {{ ?subject wdt:P155 <{0}> . }} 

    # Exclude entities related to the predicate "field of work" (wdt:P101)
    FILTER NOT EXISTS {{ ?subject wdt:P101 <{0}> . }} 

    # Exclude entities related to the predicate "is a list of" (wdt:P360)
    FILTER NOT EXISTS {{ ?subject wdt:P360 <{0}> . }} 

    # Exclude entities related to the predicate "commemorates" (wdt:P547)
    FILTER NOT EXISTS {{ ?subject wdt:P547 <{0}> . }} 

    # Exclude entities related to the predicate "depicts" (wdt:P180)
    FILTER NOT EXISTS {{ ?subject wdt:P180 <{0}> . }} 

    # Exclude entities related to the predicate "main subject" (wdt:P921)
    FILTER NOT EXISTS {{ ?subject wdt:P921 <{0}> . }} 

    # Exclude entities related to the predicate "template has topic" (wdt:P1423)
    FILTER NOT EXISTS {{ ?subject wdt:P1423 <{0}> . }} 

    # Exclude entities related to the predicate "narrative motif" (wdt:P6962)
    FILTER NOT EXISTS {{ ?subject wdt:P6962 <{0}> . }}

    ### Exclude entities with labels containing numeric characters (potential dates)
    FILTER (!REGEX(?subject_label, "[0-9]"))

    # Exclude entities with a country statement (wdt:P17)
    FILTER NOT EXISTS {{ ?subject wdt:P17 [] }}

    # Exclude entities related to a Wikimedia project page (wd:Q14204246)
    FILTER NOT EXISTS {{ ?subject wdt:P31 wd:Q14204246 }}

    # Exclude entities related to a human (wd:Q5)
    FILTER NOT EXISTS {{ ?subject wdt:P31 wd:Q5 }}

    # Exclude entities related to painting (wd:Q3305213)
    FILTER NOT EXISTS {{ ?subject wdt:P31 wd:Q3305213 }}

    # Exclude entities with a mythology statement (wd:Q9134)
    FILTER NOT EXISTS {{ ?subject wdt:P361/wdt:P31 wd:Q9134 }}

    # Exclude entities subclass of to myth (wd:Q12827256)
    FILTER NOT EXISTS {{ ?subject wdt:P279 wd:Q12827256 }} 

    # Exclude entities with a coordinate location statement (wdt:P625)
    FILTER NOT EXISTS {{ ?subject wdt:P625 [] }}

    # Exclude entities related to a point in time (wdt:P585)
    FILTER NOT EXISTS {{ ?subject wdt:P585 [] }}   

    # Exclude entities related to a number of deaths (wdt:P1120)
    FILTER NOT EXISTS {{ ?subject wdt:P1120 [] }}

    # Exclude entities related to an image (wdt:P18)
    FILTER NOT EXISTS {{ ?subject wdt:P18 [] }} 

    # Exclude entities related to the predicate "commons category" (wdt:P373)
    FILTER NOT EXISTS {{ ?subject wdt:P373 [] }} 

    # Exclude entities related to the predicate "published in" (wdt:P1433)
    FILTER NOT EXISTS {{ ?subject wdt:P1433 [] }} 

    # Exclude entities related to the predicate "category contains " (wdt:P4224)
    FILTER NOT EXISTS {{ ?subject wdt:P4224 [] }} 
    
    # Exclude entities related to the predicate "location" (wdt:P276)
    FILTER NOT EXISTS {{ ?subject wdt:P276 [] }}
    
    # Exclude entities related to the predicate "start time" (wdt:P580)
    FILTER NOT EXISTS {{ ?subject wdt:P580 [] }}
    
    # Exclude entities related to the predicate "end time" (wdt:P582)
    FILTER NOT EXISTS {{ ?subject wdt:P582 [] }}
    
    # Exclude entities related to the predicate "part of" (wdt:P361)
    FILTER NOT EXISTS {{ ?subject wdt:P361 [] }}
    
    # Exclude entities related to the predicate "Freebase ID" (wdt:P646)
    FILTER NOT EXISTS {{ ?subject wdt:P646 [] }}
    
    # Exclude entities related to the predicate "Google Knowledge Graph ID" (wdt:P2671)
    FILTER NOT EXISTS {{ ?subject wdt:P2671 [] }}
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""


forward_backward = """
SELECT ?subject ?subject_label ?predicate ?predicate_label ?object ?object_label
WHERE {{
  {{
    BIND(<{0}>  AS ?subject) .
    
    <{0}> ?predicate ?object .
    ?object rdfs:label ?object_label .
    ?wd wikibase:directClaim ?predicate .
    ?wd rdfs:label ?predicate_label .
    
    FILTER (LANG(?object_label) = "en" && LANG(?predicate_label) = "en")
    
    <{0}> rdfs:label ?subject_label .
    FILTER (LANG(?subject_label) = "en")
    
    # Exclude entities related to the predicate "on focus list of Wikimedia project" (wdt:P5008)
    FILTER NOT EXISTS {{ <{0}>  wdt:P5008 ?object }} 
  }}
  UNION
  {{
    BIND(<{0}>  AS ?object) .
    
    ?subject ?predicate <{0}>  .
    ?subject rdfs:label ?subject_label .
    ?wd wikibase:directClaim ?predicate .
    ?wd rdfs:label ?predicate_label .
    
    FILTER (LANG(?subject_label) = "en" && LANG(?predicate_label) = "en") 
    
    <{0}> rdfs:label ?object_label .
    FILTER (LANG(?object_label) = "en")
    
    # Exclude entities related to the predicate "Freebase ID" (wdt:P646)
    FILTER NOT EXISTS {{ ?subject wdt:P646 [] }}
    
    # Exclude entities related to the predicate "Google Knowledge Graph ID" (wdt:P2671)
    FILTER NOT EXISTS {{ ?subject wdt:P2671 [] }}
    
    # Exclude entities related to a Wikimedia project page (wd:Q14204246)
    FILTER NOT EXISTS {{ ?subject wdt:P31 wd:Q14204246 }}
  }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""