import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output
#https://www.statworx.com/en/blog/how-to-build-a-dashboard-in-python-plotly-dash-step-by-step-tutorial/

# Load data
# Data: csv table with columns: text, publisher, date, sentiment_Bert, sentiment_Dict
df = pd.read_csv('data.csv', index_col=0, parse_dates=True)
df['date'].replace({2006 : '01/01/2006', 2007 : '01/01/2007', 2008 : '01/01/2008', 2009 : '01/01/2009', 2010 : '01/01/2010', 2011 : '01/01/2011', 2012 : '01/01/2012', 2013 : '01/01/2013', 2014 : '01/01/2014', 2015 : '01/01/2015', 2016 : '01/01/2016', 2017 : '01/01/2017', 2018 : '01/01/2018', 2019 : '01/01/2019', }, inplace = True)
df.index = pd.to_datetime(df['date'])

# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

def get_options(list_options):
    dict_list = []
    for i in list_options:
        dict_list.append({'label': i, 'value': i})
    return dict_list

options_publisher = get_options(df['publisher'].unique()) +[{'label': 'all', 'value': 'all'}]
options_sentiment = get_options(['sentiment_Bert', 'sentiment_Dict'])

app.layout = html.Div(
    children=[
        html.Div(className='row',
                 children=[
                    html.Div(className='four columns div-user-controls',
                             children=[
                                 html.H2('Sentiment Development Refugees'),
                                 html.P('Pick one or more publishers and sentiment types from the dropdown below.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(id='publisherselector', options= options_publisher,
                                                      multi=True, value=[df['publisher'].sort_values()[0]],
                                                      className='publisherselector'
                                                      ),
                                         dcc.Dropdown(id='typeselector', options= options_sentiment,
                                                      multi=True, value=['sentiment_Dict'],
                                                      className='typeselector'
                                                      ),
                                     ])
                                ]
                             ),
                    
                    html.Div(className='eight columns div-for-charts bg-grey',
                             children=[
                                 dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True)
                             ])
                              ])
        ]

)

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
                mode='lines',
                name=publisher + '_' + senti_type,
                textposition='bottom center'))
            else:
                trace1.append(go.Scatter(x=df_sub[df_sub['publisher'] == publisher].index,
                y=df_sub[df_sub['publisher'] == publisher][senti_type],
                mode='lines',
                name=publisher + '_' + senti_type, 
                textposition='bottom center'))
				
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  template='plotly_dark',
                  hovermode='x', 
                  autosize=True,
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              )}

    return figure
    

if __name__ == '__main__':
    app.run_server(debug=True)