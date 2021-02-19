import pandas as pd
import numpy as np
import plotly.graph_objects as go

def json_to_df(filepath, date_column, title_column):
	#converts json file to pandas.DataFrame
	#sets dummy_sentiment
	#input: string filepath: path to .json file, string date_column: name of the columns which includes the dates, titles/ descriptions etc. and sentiment
	#output: pandas.DataFrame with column of date, title and dummy_sentiment
	
	json_file = filepath
	json_df = pd.read_json(json_file, convert_dates=True).transpose()

	json_df = json_df[json_df[date_column].notna()]
	
	json_df = json_df[[date_column, title_column]]
	json_df['sentiment'] = np.random.uniform(-1, 1, size=len(json_df))
	json_df.rename(columns = {date_column: 'date', title_column: 'title'}, inplace = True)
	
	return json_df

def plot_sentiment_score(df, title):
	#plots the sentiment over time, shows title when hovered over points
	#input: pandas.Dataframe df: data that should be plotted, string title: title of plot
	
	fig = go.Figure()

	fig.add_trace(go.Scatter(
		x= df['date'] ,
		y= df['sentiment'] ,
		hovertext= df['title'],
		hoverinfo="text",
		mode = 'markers',
		showlegend=False
	))

	fig.update_layout(
		title=title,
		yaxis_title='Sentiment Score'
	)

	fig.show()


df = json_to_df('data//welt.json', date_column = 'last-modified', title_column = 'title')
#df.head()
plot_sentiment_score(df, 'Dummy Sentiment Scores Welt.de')