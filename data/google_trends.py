from pytrends.request import TrendReq
import matplotlib.pyplot as plt

# Initialize pytrends
pytrends = TrendReq(hl='pt-BR', tz=360)

# Define keywords
keywords = ["música", "cultura", "tendências"]

# Build payload
pytrends.build_payload(kw_list=keywords, timeframe='today 5-y', geo='BR')

# Get interest over time
data = pytrends.interest_over_time()

# Plot the data
data.plot(title="Google Trends: Música, Cultura, Tendências")
plt.show()
