import plotly
import plotly.graph_objs as go
from itertools import cycle
import directory
import my_logger as l


def plot_QA(data, plots, dirPath):
    rl = l.RuntimeLogger(dirPath)
    rl.info("plot_QA start")
    graphs_path = directory.joinPath([dirPath,'graphs'])
    directory.createPath(graphs_path)

    rl.info("plot_QA prepare data")
    time_points = []
    rl.debug("data " + str(data))
    for seriesDate in data['seriesIndex']:
        date = str(seriesDate)
        time_points.append(date[:4] + '-' + date[4:6] + '-' + date[6:8])

    rl.debug("time_points: " + str(time_points))

    rl.info("plot_QA calculate averages across slices")

    rl.info("plot_QA prepare plots")
    time_points_sorted = sorted(time_points)
    rl.debug("time_points_sorted: " + str(time_points_sorted))
    time_point_sorted_idxs = sorted(range(len(time_points)), key=lambda k: time_points[k])
    time_points_rev = time_points_sorted[::-1]  # time points reversed
    range_colors = {'FWHMX': 'rgba(25,87,194,0.6)', 'FWHMZ': 'rgba(10,160,55,0.6)', 'FWHMY': 'rgba(235,195,21,0.6)'}
    for plot_id in plots:
        plot_data = []

        # Prepare each data trace
        for idx, data_name in enumerate(plots[plot_id]['attributes']):
            # Create a trace
            trace = go.Scatter(
                x=time_points,
                y=data[data_name],
                mode='lines+markers',
                name=data_name,
                legendgroup=data_name,
                line=dict(width=3),
                # marker=dict(size=10,symbol="circle-open-dot") #causes slider to disappear
                showlegend=True,
            )
            plot_data.append(trace)

        # Prepare range traces if exist
        for idx, val in enumerate(plots[plot_id]['range']):
            data_name, lower_bound, upper_bound = val
            # Create a trace of ranges
            upper_bound_data = list(data[upper_bound][i] for i in time_point_sorted_idxs)
            lower_bound_data = list(data[lower_bound][i] for i in time_point_sorted_idxs)
            try:
                fillcolor = range_colors[data_name]
            except:
                fillcolor = 'rgba(0,100,80,0.2)'

            trace = go.Scatter(
                x=time_points_sorted + time_points_rev,
                y=upper_bound_data + lower_bound_data[::-1],
                fill='tozerox',
                fillcolor=fillcolor,
                showlegend=True,
                name=data_name +" range",
                hoveron="points+fills",
                legendgroup=plots[plot_id]['attributes'][idx]
            )
            plot_data.append(trace)

        # Initialize layout
        layout = dict(
            # title=plots[plot_id]['title'], #included in html dashboard
            # font=dict(size=19, color='#777'),
            # margin=go.Margin(r=20, l=100,
            #                b=75, t=175),
            legend=dict(
                y=0.5,
                # font=dict(size=20),
                yanchor="auto"
            ),
            showlegend=True,
            # images=[
            #     dict(
            #         source="images/ON_logo.png",
            #         xref="paper", yref="paper",
            #         x=0.0, y=1.10,
            #         sizex=0.3, sizey=0.3,
            #         xanchor="left", yanchor="bottom"
            #     ),
            #     dict(
            #         source="images/logo_Malopolska_Centro_Biotechnology.jpg",
            #         xref="paper", yref="paper",
            #         x=1, y=1.10,
            #         sizex=0.3, sizey=0.3,
            #         xanchor="right", yanchor="bottom"
            #     )
            # ]
        )

        if plot_id == 4: # the subplot plot
            figure = plotly.tools.make_subplots(rows=3, cols=1, shared_xaxes=True)
            subplot_positions = cycle(plots[plot_id]['subplots'])
            for idx, trace in enumerate(plot_data):
                subplot_position = next(subplot_positions)
                figure.append_trace(trace, subplot_position[0], subplot_position[1])
            figure.update(layout=go.Layout(layout))
            figure['layout']['yaxis1'].update(title=plots[plot_id]['ytitle'])
            figure['layout']['yaxis2'].update(title=plots[plot_id]['ytitle'])
            figure['layout']['yaxis3'].update(title=plots[plot_id]['ytitle'])
        else:
            #add axis labels and selectors to all other subplots
            layout.update(
                xaxis=dict(
                    rangeslider=dict(
                        bordercolor="#aaa",
                        thickness=0.1,
                        bgcolor="#ddd",
                        borderwidth=3,
                        visible=True
                    ),
                    type='date',
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1,
                                 label='1m',
                                 step='month',
                                 stepmode='backward'),
                            dict(count=6,
                                 label='6m',
                                 step='month',
                                 stepmode='backward'),
                            dict(count=1,
                                 label='YTD',
                                 step='year',
                                 stepmode='todate'),
                            dict(count=1,
                                 label='1y',
                                 step='year',
                                 stepmode='backward'),
                            dict(step='all')
                        ])
                    )
                ),
                yaxis=dict(
                    title=plots[plot_id]['ytitle'],
                    # titlefont=dict(size=20)
                ),
            )
            figure = go.Figure(data=plot_data, layout=go.Layout(layout))
            rl.info("plot_QA " + plots[plot_id]['title'] + " done")

        auto_open = False #do not open the web browser upon saving
        file_path = directory.joinPath([graphs_path,'QA_results' + str(plot_id) + '.html'])
        plotly.offline.plot(figure, filename=file_path, show_link=False, auto_open=auto_open)
        rl.info("plot_QA; file " + file_path + " generated")
    template_source_path = directory.joinPath([directory.getFileDirectory(__file__),'graphs','plotly_dashboard'])
    template_destination_path = directory.joinPath([graphs_path,'plotly_dashboard'])
    directory.copy_folder_contents(template_source_path,template_destination_path)
    rl.info("plot_QA end; copied template")