import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
#https://www.statworx.com/en/blog/how-to-build-a-dashboard-in-python-plotly-dash-step-by-step-tutorial/

def dash_plot(filepath):
	# Load data
	df = pd.read_json(filepath, convert_dates=True ).transpose()
	df.index = pd.to_datetime(df['date'])

	# Initialize the app
	app = dash.Dash(__name__)
	app.config.suppress_callback_exceptions = True

	#get options for dropdowns
	def get_options(list_options):
	    dict_list = []
	    for i in list_options:
	        dict_list.append({'label': i, 'value': i})
	    return dict_list

	options_publisher = get_options(df['publisher'].unique()) +[{'label': 'all', 'value': 'all'}]
	options_sentiment = get_options(['sentiment_sentiws', 'sentiment_generic_sentibert', 'sentiment_finetuned_sentibert'])

	#set layout of app
	app.layout = html.Div(
	    children=[
		html.Div(className='row',
		         children=[
		            html.Div(children=[
		                         html.H2('Sentiment Development Refugees'),
		                         html.P('Pick one or more publishers and sentiment types from the dropdown below.'),
		                         html.Div(
		                             children=[
		                                 dcc.Dropdown(id='publisherselector', options= options_publisher,
		                                              multi=True, value=['all'],
		                                              className='publisherselector'
		                                              ),
		                                 dcc.Dropdown(id='typeselector', options= options_sentiment,
		                                              multi=True, value=['sentiment_sentiws'],
		                                              className='typeselector'
		                                              ),
		                             ])
		                        ]
		                     ),
		            
		            html.Div(children=[
		                         dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True)
		                     ])
		                      ])
		])


	# Callback for timeseries sentiment
	@app.callback(Output('timeseries', 'figure'),
		      Input('publisherselector', 'value'), Input('typeselector', 'value'))
	def update_graph(publishers, types):
	    trace1 = []
	    df_sub = df
	    for publisher in publishers:
	        for senti_type in types:
	            if publisher == 'all':
	                trace1.append(go.Scatter(x=df_sub.index, 
	                y=df_sub[senti_type],
	                mode='markers',
	                name=publisher + '_' + senti_type,
	                textposition='bottom center',
	                hoverinfo = 'text',
	                hovertext = df_sub['title']))
	                #add trendline
	                fig = px.scatter(df_sub, x=df_sub.index, y=df_sub[senti_type], trendline = 'lowess')
	                trace1.append(fig.data[1])
	            else:
	                df_sub2 = df_sub[df_sub['publisher'] == publisher]
	                trace1.append(go.Scatter(x=df_sub[df_sub['publisher'] == publisher].index,
	                y=df_sub[df_sub['publisher'] == publisher][senti_type],
	                mode='markers',
	                name=publisher + '_' + senti_type,
	                textposition='bottom center',
	                hoverinfo = 'text',
	                hovertext = df_sub[df_sub['publisher'] == publisher]['title']))
	                #add trendline
	                fig = px.scatter(df_sub2, x=df_sub2.index, y=df_sub2[senti_type], trendline = 'lowess')
	                trace1.append(fig.data[1]) 
					
	    traces = [trace1]
	    data = [val for sublist in traces for val in sublist]
	    figure = {'data': data,
		      'layout': go.Layout(
		          template='plotly_dark',
		          autosize=True,
		          xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
		      )}
	    
	    return figure
    
	app.run_server(debug=True)