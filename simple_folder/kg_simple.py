from dotenv import load_dotenv
import os
from neo4j import GraphDatabase

load_dotenv()

AURA_INSTANCENAME = os.environ["AURA_INSTANCENAME"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USERNAME = os.environ["NEO4J_USERNAME"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]
NEO4J_DATABASE = os.environ["NEO4J_DATABASE"]
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)

driver = GraphDatabase.driver(NEO4J_URI, auth=AUTH, database=NEO4J_DATABASE)

def connect_and_query():
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("MATCH (n) RETURN count(n)")
            count = result.single().value()
            print(f"Number of nodes {count}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

def create_entities(tx):
    tx.run("MERGE (p:Person {name: 'Albert Einstein'})")
    tx.run("MERGE (p: Subject {name: 'Physics'})")    
    tx.run("MERGE (n: NobelPrize {name: 'Nobel Prize in Physics'})")
    tx.run("MERGE (g: Country {name: 'Germany'})")
    tx.run("MERGE (u: Country {name: 'USA'})")

def create_relationships(tx):
    tx.run("""
           MATCH (a:Person {name: 'Albert Einstein'}), (p:Subject {name: 'Physics'})
           MERGE (a)-[:STUDIED]->(p)
           """)
    
    tx.run("""
           MATCH (a:Person {name: 'Albert Einstein'}), (n:NobelPrize {name: 'Nobel Prize in Physics'})
           MERGE (a)-[:WON]->(n)
           """)

    tx.run("""
           MATCH (a:Person {name: 'Albert Einstein'}), (g:Country {name: 'Germany'})
           MERGE (a)-[:BORN_IN]->(g)
           """)
    
    tx.run("""
           MATCH (a:Person {name: 'Albert Einstein'}), (u:Country {name: 'USA'})
           MERGE (a)-[:DIED_IN]->(u)
           """)
    
def query_graph_simple(cypher_query):
    driver = GraphDatabase.driver(NEO4J_URI, auth=AUTH)
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(cypher_query)
            for record in result:
                print(record["name"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

def query_graph(cypher_query):
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(cypher_query)
            for record in result:
                print(record["path"])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

def build_knowledge_graph():
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            session.execute_write(create_entities)
            session.execute_write(create_relationships)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.close()

einstein_query = """
MATCH path=(a:Person {name:'Albert Einstein'})-[:STUDIED]->(p:Subject)
RETURN path
UNION
MATCH path=(a:Person {name:'Albert Einstein'})-[:WON]->(n:NobelPrize)
RETURN path
UNION
MATCH path=(a:Person {name:'Albert Einstein'})-[:BORN_IN]->(g:Country)
RETURN path
UNION
MATCH path=(a:Person {name:'Albert Einstein'})-[:DIED_IN]->(u:Country)
RETURN path
"""

simple_query = """
MATCH (n)
RETURN n.name AS name
"""

if __name__ == "__main__":
    #build_knowledge_graph()
    #query_graph_simple(simple_query)
    query_graph(einstein_query)
