
import plotly.graph_objects as go
import numpy as np

np.random.seed(0)

f = lambda x,y: np.sin(np.sqrt(x**2 + y**2))*1/4

# Surface data
x = np.linspace(0, 5, 50)
y = np.linspace(0, 5, 50)
X, Y = np.meshgrid(x, y)
Z = f(X,Y)

fig = go.Figure()

# Add surface
fig.add_trace(go.Surface(z=Z, x=X, y=Y, opacity=0.7, colorscale="peach"))

# Scatter point
colors = ["red", "orange", "yellow", "green", "blue"]
n_points = 50
center_x = 3
center_y = 3
sigma = 0.3

center_x_log = []
center_y_log = []


for i, color in enumerate(colors):
    center_x_log.append(center_x)
    center_y_log.append(center_y)

    scatter_x = np.random.randn(n_points) * sigma + center_x
    scatter_y = np.random.randn(n_points) * sigma + center_y
    
    scatter_z = f(scatter_x, scatter_y) + .025

    # Add scatter point
    fig.add_trace(go.Scatter3d(x=scatter_x, y=scatter_y, z=scatter_z, opacity=0.7, mode='markers', marker=dict(size=5, color=color)))

    new_center = np.argmax(scatter_z)
    center_x = scatter_x[new_center]
    center_y = scatter_y[new_center]

fig.add_trace(go.Scatter3d(x=center_x_log, y=center_y_log, z=f(np.array(center_x_log), np.array(center_y_log)) + .025, marker=dict(size=5, color="green", opacity=0.0), line=dict(color='purple', width=5, dash="dash")))

fig.show()
