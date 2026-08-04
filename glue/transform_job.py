import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'data_file_path', 'output_path'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

df = spark.read.csv(args['data_file_path'], header=True, inferSchema=False)

df_clean = df \
    .withColumnRenamed('timestamp', 'created_at') \
    .withColumn('amount', df['amount'].cast('decimal(12,2)'))

df_clean.write.csv(args['output_path'], header=True, mode='overwrite')
