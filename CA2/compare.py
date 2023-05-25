import time
import psutil
import mysql.connector
from cassandra.cluster import Cluster
import pandas as pd
from cassandra import ConsistencyLevel
# Establish connections to MySQL and Cassandra databases
mysql_conn  = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="twitter_sent"
    )

cluster = Cluster(["127.0.0.1"], port = 9046)
cassandra_session = cluster.connect()
cassandra_session.set_keyspace("sd")
# Create test data
test_data = [
    {'date': '2023-05-01', 'sentiment': '0.8'},
    {'date': '2023-05-02', 'sentiment': '0.5'},
    {'date': '2023-05-03', 'sentiment': '0.6'},
    # Add more data points here
]

# Create an empty DataFrame to store the metrics
metrics_df = pd.DataFrame(columns=["Database", "CPU_utility", "Memory_usage", "Insertion_time", "Creation_time", "Deletion_time", "Updation_time"])

# Function to measure CPU utility and memory resource
def measure_cpu_memory():
    cpu_utility = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    return cpu_utility, memory_usage
from cassandra.query import BatchStatement
from cassandra.query import SimpleStatement
# Function to measure insertion time
def measure_insertion_time(database, data):
    if database == "MySQL":
        start_time = time.time()
        # Perform insertion in MySQL
        cursor = mysql_conn.cursor()
        query = "INSERT INTO PreprocessedSD (Date, Sentiment) VALUES (%s, %s)"
        cursor.executemany(query, [(item['date'], item['sentiment']) for item in data])
        mysql_conn.commit()
        end_time = time.time()
    elif database == "Cassandra":
        start_time = time.time()
        # Perform insertion in Cassandra
        batch = BatchStatement(consistency_level=ConsistencyLevel.LOCAL_ONE)
        for row in data:
            query = """
            INSERT INTO PreprocessedSD (Date, Sentiment) VALUES (?, ?)
            """
            statement = SimpleStatement(query, consistency_level=ConsistencyLevel.LOCAL_ONE)
            batch.add(statement, (row['date'], row['sentiment']))
        cassandra_session.execute(batch, timeout=None)
        end_time = time.time()

    insertion_time = end_time - start_time
    return insertion_time

# Function to measure creation time
def measure_creation_time(database):
    if database == "MySQL":
        start_time = time.time()
        # Perform table creation in MySQL
        cursor = mysql_conn.cursor()
        query = "CREATE TABLE IF NOT EXISTS  PreprocessedSD (Date VARCHAR(255), Sentiment VARCHAR(255))"
        cursor.execute(query)
        end_time = time.time()
    elif database == "Cassandra":
        start_time = time.time()
        # Perform table creation in Cassandra
        query = "CREATE TABLE  IF NOT EXISTS  PreprocessedSD (Date TEXT, Sentiment TEXT, PRIMARY KEY (Date))"
        cassandra_session.execute(query, timeout=None)
        end_time = time.time()

    creation_time = end_time - start_time
    return creation_time

# Function to measure deletion time
def measure_deletion_time(database):
    if database == "MySQL":
        start_time = time.time()
        # Perform record deletion in MySQL
        cursor = mysql_conn.cursor()
        query = "DELETE FROM PreprocessedSD"
        cursor.execute(query)
        mysql_conn.commit()
        end_time = time.time()
    elif database == "Cassandra":
        start_time = time.time()
        # Perform record deletion in Cassandra
        query = "TRUNCATE PreprocessedSD"
        cassandra_session.execute(query,  timeout=None)
        end_time = time.time()

    deletion_time = end_time - start_time
    return deletion_time

# Function to measure updation time
def measure_updation_time(database, data):
    if database == "MySQL":
        start_time = time.time()
        # Perform record updation in MySQL
        cursor = mysql_conn.cursor()
        query = "UPDATE PreprocessedSD SET Sentiment = %s WHERE Date = %s"
        cursor.executemany(query, [(item['date'], item['sentiment']) for item in data])
        mysql_conn.commit()
        end_time = time.time()
    elif database == "Cassandra":
        start_time = time.time()
        # Perform record updation in Cassandra
        query = "UPDATE PreprocessedSD SET Sentiment = ? WHERE Date = ?"
        prepared_query = cassandra_session.prepare(query)
        batch = cassandra_session.batch()
        for item in data:
            batch.add(prepared_query, (item[1], item[0]))
        cassandra_session.execute(batch, timeout=None)
        end_time = time.time()

    updation_time = end_time - start_time
    return updation_time

# Measure metrics for MySQL

print('MYSQL')
cpu_utility, memory_usage = measure_cpu_memory()
creation_time = measure_creation_time("MySQL")
print('creation_time')
insertion_time = measure_insertion_time("MySQL", test_data)
print('insertion_time')
updation_time = measure_updation_time("MySQL", test_data)
print('updation_time')
deletion_time = measure_deletion_time("MySQL")
print('deletion_time')

# Store MySQL metrics in DataFrame
metrics_df = metrics_df.append({
    "Database": "MySQL",
    "CPU_utility": cpu_utility,
    "Memory_usage": memory_usage,
    "Insertion_time": insertion_time,
    "Creation_time": creation_time,
    "Deletion_time": deletion_time,
    "Updation_time": updation_time
}, ignore_index=True)

# Measure metrics for Cassandra

print('Cassandra')
cpu_utility, memory_usage = measure_cpu_memory()
creation_time = measure_creation_time("Cassandra")
print('creation_time')
insertion_time = measure_insertion_time("Cassandra", test_data)
print('insertion_time')
updation_time = measure_updation_time("Cassandra", test_data)
print('updation_time')
deletion_time = measure_deletion_time("Cassandra")
print('deletion_time')

# cpu_utility, memory_usage = measure_cpu_memory()
# insertion_time = measure_insertion_time("Cassandra", test_data)
# creation_time = measure_creation_time("Cassandra")
# deletion_time = measure_deletion_time("Cassandra")
# updation_time = measure_updation_time("Cassandra", test_data)

# Store Cassandra metrics in DataFrame
metrics_df = metrics_df.append({
    "Database": "Cassandra",
    "CPU_utility": cpu_utility,
    "Memory_usage": memory_usage,
    "Insertion_time": insertion_time,
    "Creation_time": creation_time,
    "Deletion_time": deletion_time,
    "Updation_time": updation_time
}, ignore_index=True)

# Print the metrics DataFrame
print(metrics_df)
