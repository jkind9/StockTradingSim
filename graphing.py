import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

def output_graph(df):
    n_series = df.shape[1]     
    # Choose a colormap and generate colors
    colormap = plt.cm.viridis
    colors = [colormap(i) for i in np.linspace(0, 1, n_series)]

    # Create a large figure to hold all subplots
    fig, axs = plt.subplots(n_series, 1, figsize=(8, 4 * n_series))

    # Iterate through the DataFrame columns and create subplots
    for i, col in enumerate(df.columns):
        ax = axs[i] if n_series > 1 else axs  # Handle case for single series
        ax.plot(df[col], label=col, color=colors[i])
        ax.yaxis.grid(True)  # Add horizontal gridlines
        ax.xaxis.grid(True)  # Add horizontal gridlines

        ax.set_ylabel(col)
        ax.legend()

    # Adjust layout
    plt.tight_layout()

    # Save the figure to an image file
    fig.savefig('OutputGraph.jpg')

    # Optionally close the figure
    plt.close(fig)


def update_graph(ax, line, new_data):
    """
    Updates the graph with new data and adjusts the axes limits to fit all data points.

    Parameters:
    ax (matplotlib.axes.Axes): The axis to update.
    line (matplotlib.lines.Line2D): The line object to update.
    new_data (tuple): A tuple (new_x, new_y) representing the new data point.
    """
    # Update the line data
    line.set_xdata(np.append(line.get_xdata(), new_data[0]))
    line.set_ydata(np.append(line.get_ydata(), new_data[1]))

    # Adjust the x and y limits to fit all data points
    ax.set_xlim(min(line.get_xdata()), max(line.get_xdata()))
    ax.set_ylim(min(line.get_ydata()), max(line.get_ydata()))

    # Redraw the figure to show the updated line and axes
    ax.relim()  # Recalculate limits
    ax.autoscale_view()  # Rescale the view
    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()

def update_or_add_line(ax, gradient, intercept, line_label='Updated Line'):
    """
    Updates or adds a line to a specified matplotlib axis (subplot) based on the gradient and y-intercept.
    Ensures only one line with the given label exists on the axis.

    Parameters:
    ax (matplotlib.axes.Axes): The axis to update/add the line to.
    gradient (float): The gradient (slope) of the line.
    intercept (float): The y-intercept of the line.
    line_label (str): Label for the line.
    """
    # Get the current x-limits of the axis to determine the range for plotting the line
    x_vals = np.array(ax.get_xlim())
    y_vals = intercept + gradient * x_vals

    # Check if a line with the given label already exists
    line_exists = False
    for line in ax.get_lines():
        if line.get_label() == line_label:
            # Update the existing line
            line.set_xdata(x_vals)
            line.set_ydata(y_vals)
            line_exists = True
            break

    # If the line doesn't exist, create a new one
    if not line_exists:
        ax.plot(x_vals, y_vals, label=line_label)

    # Redraw the axis to show the updated/new line
    ax.relim()  # Recalculate limits
    ax.autoscale_view()  # Rescale the view
    ax.legend()  # Update the legend

def add_vertical_line(ax, x, color='red'):
    ax.axvline(x=x, color=color, linestyle='--')
