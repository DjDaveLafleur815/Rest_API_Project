from neo4j import GraphDatabase
import requests # type: ignore
import json

# Fonction pour établir une connexion à Neo4j
def connect_to_neo4j(uri, user, password):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

# Fonction pour récupérer les données de l'API REST
def fetch_data_from_api(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()['results']
    else:
        response.raise_for_status()

# Fonction pour insérer des données JSON dans Neo4j
def insert_data(driver, data):
    with driver.session() as session:
        for record in data:
            session.write_transaction(create_user_node, record)

# Transaction Cypher pour créer un nœud utilisateur
def create_user_node(tx, record):
    query = """
    CREATE (u:User {
        uuid: $uuid,
        first_name: $first_name,
        last_name: $last_name,
        email: $email,
        username: $username,
        password: $password,
        gender: $gender,
        city: $city,
        country: $country
    })
    """
    tx.run(query,
           uuid=record['login']['uuid'],
           first_name=record['name']['first'],
           last_name=record['name']['last'],
           email=record['email'],
           username=record['login']['username'],
           password=record['login']['password'],
           gender=record['gender'],
           city=record['location']['city'],
           country=record['location']['country'])

# Fonction pour afficher les données insérées
def display_data(driver):
    with driver.session() as session:
        result = session.read_transaction(get_data)
        for record in result:
            print(record)

# Transaction Cypher pour récupérer les données
def get_data(tx):
    query = """
    MATCH (u:User)
    RETURN u.uuid AS uuid, u.first_name AS first_name, u.last_name AS last_name, u.email AS email, u.username AS username, u.gender AS gender, u.city AS city, u.country AS country
    """
    result = tx.run(query)
    return result

# URL de l'API
api_url = "https://randomuser.me/api/?results=100"

# Récupérer les données de l'API
data = fetch_data_from_api(api_url)

# Connexion à la base de données Neo4j
uri = "bolt://localhost:7687"
user = "neo4j"
password = "your_password"

driver = connect_to_neo4j(uri, user, password)

# Insérer les données JSON dans Neo4j
insert_data(driver, data)

# Afficher les données insérées
display_data(driver)

# Fermer la connexion
driver.close()
