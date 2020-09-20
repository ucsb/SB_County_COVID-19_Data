# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 19:42:54 2020

@author: bdaet
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import re
from fbprophet import Prophet
from fbprophet.plot import plot_plotly, plot_components_plotly

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#dictionary of colors for app
#original background color was #111111
colors = {'background': '#495757',
          'text': '#7FDBFF',
          'fbplot_background': '#878686'}

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('https://raw.githubusercontent.com/bryandaetz1/SB_County_COVID-19_Data/master/CSV_Files/cases_by_area_9-19-20.csv')

#converting date column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

#creating new column with cleaned up geographic areas
area_list = []
for area in df['Geographic Area']:
    if area == 'Total*' or area =='Total**':
        x = 'Total'
    elif area == 'Out of County' or area == 'Pending':
        x = area
    else:
        x = re.sub('[a-z]+','',area).strip().split('  ')[0]
    area_list.append(x)
    
df['Geographic_Area'] = area_list
df.drop('Geographic Area', axis = 1, inplace=True)

#dataframe for active cases by region visualization
area_df = df.loc[(df['Geographic_Area'] != 'Total') &
                 (df['Geographic_Area'] != 'Pending') &
                 (df['Geographic_Area'] != 'Out of County')]

#dataframe for fbprophet prediction/visualization
#fb_df = df[df['Geographic_Area'] == 'Total'][['Date','Still infectious by Region']]
#fb_df.columns = ['ds','y']

#removing weekends
#fb_df_weekdays = fb_df[fb_df['ds'].dt.dayofweek < 5]

#fitting the fbprophet model
#prophet = Prophet()
#prophet.fit(fb_df_weekdays)

#making dataframe of future dates, 30 days into future
#future = prophet.make_future_dataframe(periods = 30)
#future_weekdays = future[future['ds'].dt.dayofweek < 5]

#generating forecast for future dates
#forecast = prophet.predict(future_weekdays)

#plotting forecast
#fig1 = plot_plotly(prophet, forecast)

#fig1.update_layout(paper_bgcolor = colors['background'],
                #   plot_bgcolor = colors['background'],
                #   font = {'color':colors['text']},
                #   xaxis={'title': 'Date'},
                #   yaxis={'title': 'Number of Active Cases'})

#fig1.update_traces(marker = {'color': 'LightSkyBlue'})

#plotting forecast components
#fig2 = plot_components_plotly(prophet, forecast)
#fig2.update_layout(paper_bgcolor = colors['background'],
                  # plot_bgcolor = colors['background'],
                  # font = {'color':colors['text']})



app.layout = html.Div(style = {'backgroundColor': colors['background']},
    children = [
    html.H1('COVID-19 Cases by Region',style = {'textAlign':'center', 'color':colors['text']}), 
    dcc.RadioItems(id = 'radio-items',
                   options = [{'label':'New Cases Per Day', 'value':'Daily Cases'},
                              {'label':'Total Confirmed Cases', 'value':'Total\xa0 Confirmed Cases'},
                              {'label':'Recovered Patients', 'value':'Recovered by Region'},
                              {'label':'Active Cases', 'value':'Still infectious by Region'},
                              {'label':'Number of Deaths', 'value':'Number of Deaths'}],
                   value = 'Still infectious by Region',
                   style = {'color': colors['text']}),
    
    dcc.Graph(id='cases-by-region'),    #figure for graph will be determined by app callback
    
    html.H1(id = 'fb_header',
            children = 'Forecast for Total Number of Active Cases in Santa Barbara County',
            style = {'textAlign':'center', 'color':colors['text']}),
    
    dcc.Graph(id='fbprophet-prediction')#,
              
                                                                              
    #html.H2('Seasonality Trends for Forecast',
    #        style = {'textAlign':'center', 'color':colors['text']})#,
    
   #dcc.Graph(id='fbprophet-components')
              #figure = fig2)
])


#function to make region graph interactive
@app.callback(
    Output(component_id='cases-by-region', component_property='figure'),
    [Input(component_id='radio-items', component_property='value')])

def create_graph(value):
    figure={
        'data': [
            go.Scatter(
                x = area_df[area_df['Geographic_Area'] == i]['Date'],
                y = area_df[area_df['Geographic_Area'] == i][value],
                text = area_df[area_df['Geographic_Area'] == i][['Geographic_Area', value]],
                mode='lines',
                opacity=0.8,
                marker={'size': 15,
                            'line': {'width': 0.5, 'color': 'white'}},
                name=i) for i in area_df.Geographic_Area.unique()
            ],
        'layout': go.Layout(
            paper_bgcolor = colors['background'],
            plot_bgcolor = colors['background'],
            font = {'color':colors['text']},
            xaxis={'title': 'Date'},
            height = 750,
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': -0.75},
            hovermode='closest')
        }
    return figure


#function to control header for fb prophet forecast section
@app.callback(
    Output(component_id='fb_header', component_property='children'),
    [Input(component_id='radio-items',component_property='value')])

def create_header(value):
    
    header_options = {'Daily Cases':'New Cases Per Day',
                     'Total\xa0 Confirmed Cases':'Total Confirmed Cases',
                     'Recovered by Region':'Recovered Patients',
                     'Still infectious by Region':'Active Cases',
                     'Number of Deaths':'Number of Deaths'}
    
    header = '30 Day Forecast for ' + header_options[value] + ' in Santa Barbara County'
    
    return header


#function to make fb prophet forecast interactive
@app.callback(
    Output(component_id='fbprophet-prediction', component_property='figure'),
    [Input(component_id='radio-items', component_property='value')])

def create_forecasts(value):
    #dataframe for fbprophet prediction/visualization
    fb_df = df[df['Geographic_Area'] == 'Total'][['Date', value]]
    fb_df.columns = ['ds','y']
    
    #removing any non-numberical characters
    fb_df['y'] = fb_df['y'].apply(lambda x: int(re.sub('[^0-9]','',str(x))))

    #removing weekends
    fb_df_weekdays = fb_df[fb_df['ds'].dt.dayofweek < 5]

    #fitting the fbprophet model
    prophet = Prophet()
    prophet.fit(fb_df_weekdays)

    #making dataframe of future dates, 30 days into future
    future = prophet.make_future_dataframe(periods = 30)
    future_weekdays = future[future['ds'].dt.dayofweek < 5]

    #generating forecast for future dates
    forecast = prophet.predict(future_weekdays)
    
    #dictionary of title options based on radio items feature to be used in app callbacks for fb prophet section
    title_options = {'Daily Cases':'New Cases Per Day',
                     'Total\xa0 Confirmed Cases':'Total Confirmed Cases',
                     'Recovered by Region':'Recovered Patients',
                     'Still infectious by Region':'Active Cases',
                     'Number of Deaths':'Number of Deaths'}
    #plotting forecast
    fig1 = plot_plotly(prophet, forecast)

    fig1.update_layout(paper_bgcolor = colors['background'],
                       plot_bgcolor = colors['background'],
                       font = {'color':colors['text']},
                       xaxis={'title': 'Date'},
                       yaxis={'title': title_options[value]},
                       width = 1000)

    fig1.update_traces(marker = {'color': 'LightSkyBlue'})
    
    
    return fig1
    

if __name__ == '__main__':
    app.run_server()