import plotly
import plotly.graph_objs as go


# class Plot(plotly):
#     def __init__(self):
#
#     def setX
#
# class DataSet:
#     def __init__(self):
#         self.plotable_data = [go.Scatter()]
#
#     def setX(self,x_list):
#         self.x=x_list

def plot_QA(data):

    plot_data = []
    time_points =  data['seriesIndex']

    for key in data:
        # Create a trace
        trace = go.Scatter(
            x=time_points,
            y=data[key],
            mode='lines+markers',
            name=key
            # ,showlegend=True
            # ,line=dict(color='rgb(180,180,180)', width=3)
            # ,marker=dict(color='rgb(80,80,80)', size=7)
        )
        plot_data.append(trace)



    layout = go.Layout(  # all "layout" attributes: /python/reference/#layout
        title="simple example",  # more about "layout's" "title": /python/reference/#layout-title
        xaxis=dict(title="time"),
        legend=dict(
            y=0.5,
            font=dict(size=16),
            yanchor="auto"
            ),
        showlegend=True
    )

    figure = go.Figure(data=plot_data, layout=layout)
    # Plot and embed in ipython notebook!


    plotly.offline.plot(figure, filename='QA_results')
