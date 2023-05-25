from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import RegexTokenizer
from pyspark.ml.feature import PorterStemmer
from pyspark.sql.types import StringType
import re
# Initialize SparkSession
spark = SparkSession.builder.getOrCreate()

# Define preprocessing functions
def lower_case(text):
    """Convert text to lowercase."""
    return text.lower()

def remove_stopwords(text):
    """Remove stopwords from text."""
    stopwords = ['stopword1', 'stopword2', 'stopword3']  # Define your stopwords
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)

def stem_text(text):
    """Apply stemming to text."""
    stemmer = PorterStemmer()
    words = text.split()
    stemmed_words = [stemmer.stem(word) for word in words]
    return ' '.join(stemmed_words)

def remove_special_characters(text):
    """Remove emojis and special characters from text."""
    # Define regex patterns for emojis and special characters
    emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]+'
    special_chars_pattern = r'[^a-zA-Z0-9\s]'

    # Remove emojis
    text = re.sub(emoji_pattern, '', text)

    # Remove special characters
    text = re.sub(special_chars_pattern, '', text)
    return text

def remove_url_hashtags(text):
    """Remove URLs and hashtags from text."""
    # Define regex patterns for URLs and hashtags
    url_pattern = r'http\S+'
    hashtag_pattern = r'#[\w_]+'

    # Remove URLs
    text = re.sub(url_pattern, '', text)

    # Remove hashtags
    text = re.sub(hashtag_pattern, '', text)
    return text

# Register UDFs
lower_case_udf = udf(lower_case, StringType())
remove_stopwords_udf = udf(remove_stopwords, StringType())
stem_text_udf = udf(stem_text, StringType())
remove_special_chars_udf = udf(remove_special_characters, StringType())
remove_url_hashtags_udf = udf(remove_url_hashtags, StringType())

# Read data from MySQL
df = spark.read.format("jdbc").option("url", "jdbc:mysql://localhost:3306/twitter_sent") \
    .option("driver", "com.mysql.jdbc.Driver").option("dbtable", "SocialDilemma") \
    .option("user", "root").option("password", "root").load()

# Apply preprocessing steps on text column
df = df.withColumn("lowercased_text", lower_case_udf("text"))
df = df.withColumn("stopwords_removed_text", remove_stopwords_udf("lowercased_text"))
df = df.withColumn("stemmed_text", stem_text_udf("stopwords_removed_text"))
