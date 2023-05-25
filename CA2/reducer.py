#!/usr/bin/env python

import sys
import mysql.connector

def reducer():
    # Connect to MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="twitter_sentiment"
    )
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("CREATE TABLE IF NOT EXISTS tweets (text TEXT, class_label INT, date text)")

    # Read input from standard input
    for line in sys.stdin:
        # Remove leading/trailing whitespaces and split the line by tabs
        line = line.strip()
        columns = line.split("\t")

        # Get the preprocessed text and encoded class label
        text = columns[0]
        class_label = int(columns[1])
        date = columns[2]
        # Insert the data into the MySQL table
        cursor.execute("INSERT INTO tweets (text, class_label, Date) VALUES (%s, %s, %s)", (text, class_label, date))

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    reducer()
