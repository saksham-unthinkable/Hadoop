from pyspark import SparkConf, SparkContext

# The following function just creates a Python dictionary which we can later use to convert 
# movie ID's to movie names while printing out the final results

def loadMovieNames():
  movieNames = {}
  with open("ml-100k/u.item",encoding="ISO-8859-1") as f:
    for line in f:
      fields = line.split('|')
      movieNames[int(fields[0])] = fields[1]
  return movieNames

# Take each line of u.data and convert it to (movieID,(rating,1.0))
# This way we can then add up all the ratings for each movie, and the 
# total number of ratings for each movie (which lets you compute the average)
def parseInput(line):
  fields = line.split()
  return (int(fields[1]),(float(fields[2]), 1.0))

if __name__ == "__main__":
  # The main script - create our SparkContext
  conf = SparkConf().setAppName("WorstMovies")
  sc = SparkContext.getOrCreate(conf = conf)

#Load up our movie ID -> movie name lookup table
movieNames = loadMovieNames()

#Load up the raw u.data file
lines = sc.textFile("hdfs:///user/maria_dev/ml-100k/u.data")

# Conert to (movieID,(rating, 1.0))
movieRatings = lines.map(parseInput)

# Reduce to (movieID, (sumOfRatings, totalRatings))
ratingTotalsAndCount = movieRatings.reduceByKey(lambda movie1, movie2: ( movie1[0] + movie2[0], movie1[1] + movie2[1] ) )

# Map to (movieID, averageRating)
averageRatings = ratingTotalsAndCount.mapValues(lambda totalAndCount : totalAndCount[0] / totalAndCount[1])

#Sort by Average Rating
sortedMovies = averageRatings.sortBy(lambda x: x[1])

# Take the top 10 results
results = sortedMovies.take(10)

#Print them out:
for result in results:
  print(movieNames[result[0]], result[1])

