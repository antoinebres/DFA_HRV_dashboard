from sub import Subscriber
from rr_utils import *
import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
import time
import plotly.graph_objs as go

# app = dash.Dash('DFA_HRV_VT1_Alpha1')
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/css/materialize.min.css"]
external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js']

app = dash.Dash(__name__,
                external_scripts=external_js,
                external_stylesheets=external_css)

app.layout = html.Div(
	[
		html.Div([
			html.H2('DFA analysis of HRV: VT1 estimation via Alpha1',
				style={'float': 'left'}),
		]),
		html.Div(children=html.Div(id='graphs'), className='row'),
		dcc.Interval(
			id='graph-update',
			interval=15*1000, # in milliseconds
			n_intervals=0
		),
	],
	className="container",
	style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000}
	)


def speedometer_fig(alpha1_val):
	return go.Figure(go.Indicator(
		mode = "gauge+number",
		value = alpha1_val,
		domain = {'x': [0, 1], 'y': [0, 1]},
		gauge = {'axis': {'range': [1.5, 0.4], 'tickvals': [1.5, 1.25, 1, .75, .5]},
			'bar': {'color': "green"},
			'steps' : [
				{'range': [0.4, 0.5625], 'color': "rgb(227,26,28)"},
				{'range': [0.5625, 0.75], 'color': "rgb(252,78,42)"},
				{'range': [0.75, 0.9375], 'color': "rgb(253,141,60)"},
				{'range': [0.9375, 1.125], 'color': "rgb(254,178,76)"},
				{'range': [1.125, 1.3125], 'color': "rgb(254,217,118)"},
				{'range': [1.3125, 1.5], 'color': "rgb(255,237,160)"},
				],
			'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 1, 'value': 0.75}},
		title = {'text': "alpha1"}))

def get_curr_alpha1_val():
	RRs = rr_sub.get_RRs()
	rest_threshold = 0.2
	activity_threshold = 0.05
	filtered_RRs = filter_RRs(RRs, rest_threshold)
	times = np.cumsum(filtered_RRs)
	df = pd.DataFrame({'timestamp': times, 'RR': filtered_RRs})
	features = compute_last_window_features(df)
	return features['alpha1']


@app.callback(dash.dependencies.Output('graphs','children'), [dash.dependencies.Input('graph-update', 'n_intervals')])
def update_graph(n):
	try:
		alpha1_val = get_curr_alpha1_val()
		return (
			html.Div(
				dcc.Graph(
					id='graphs',
					animate=True,
					figure=speedometer_fig(alpha1_val)
				),
				className='col s12'
			)
		)
	except Exception as e:
		print("exception", e)
		pass

# @app.callback(dash.dependencies.Output('graphs','children'), [dash.dependencies.Input('graph-update', 'n_intervals')])
# def update_graph(n):
# 	try:
# 		RRs = rr_sub.get_RRs()
# 		rest_threshold = 0.2
# 		activity_threshold = 0.05
# 		filtered_RRs = filter_RRs(RRs, rest_threshold)
# 		times = np.cumsum(filtered_RRs)
# 		df = pd.DataFrame({'timestamp': times, 'RR': filtered_RRs})
# 		features_df = compute_features(df)
# 		features_df['minutes'] = features_df['timestamp'] * 2 # window length
# 		data = go.Scatter(
# 			x=features_df['minutes'],
# 			y=features_df['alpha1'],
# 			name='Scatter',
# 			fill="tozeroy",
# 			fillcolor="#6897bb"
# 		)
# 		return (
# 			html.Div(
# 				dcc.Graph(
# 					id='RRs',
# 					animate=True,
# 					figure={
# 						'data': [data],
# 						'layout' : go.Layout(
# 							xaxis=dict(range=[features_df['minutes'].min(), features_df['minutes'].max()]),
# 							yaxis=dict(range=[features_df['alpha1'].min(), features_df['alpha1'].max()]),
# 							margin={'l':50,'r':1,'t':45,'b':1},
# 							title='{}'.format('RR intervals'))
# 						}
# 				),
# 				className='col s12'
# 			)
# 		)
# 	except Exception as e:
# 		print("exception", e)
# 		pass

if __name__ == '__main__':
	rr_sub = Subscriber()
	app.run_server(debug=True)