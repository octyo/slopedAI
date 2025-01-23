
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
colors = ["red", "orange", "yellow", "green"]
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

    new_center = np.argmax(scatter_z)

    # Add scatter point
    fig.add_trace(go.Scatter3d(x=np.delete(scatter_x, new_center), y=np.delete(scatter_y, new_center), z=np.delete(scatter_z, new_center), opacity=0.7, mode='markers', marker=dict(size=5, color=color)))
    fig.add_trace(go.Scatter3d(x=[center_x], y=[center_y], z=[f(center_x, center_y) + .025], opacity=0.7, mode='markers', marker=dict(size=10, color="black", symbol="cross", line=dict(color='black', width=12))))

    center_x = scatter_x[new_center]
    center_y = scatter_y[new_center]

fig.add_trace(go.Scatter3d(x=center_x_log, y=center_y_log, z=f(np.array(center_x_log), np.array(center_y_log)) + .025, marker=dict(size=5, color="green", opacity=0.0), line=dict(color='black', width=5, dash="solid")))



# fig.update_layout(
#     scene = dict(
#         xaxis = dict(nticks=4, range=[0,5],),
#         yaxis = dict(nticks=4, range=[0,5],)
#         # ,zaxis = dict(nticks=4, range=[-0.3,0.5],),
#         ),
#     width=700,
#     margin=dict(r=20, l=10, b=10, t=10))



# Default parameters which are used when `layout.scene.camera` is not provided
camera = dict(
    up=dict(x=0, y=0, z=1),
    center=dict(x=0, y=0, z=0),
    eye=dict(x=0.2*1.5, y=1.25*1.5, z=0.8*1.5)
)

fig.update_layout(scene_camera=camera)

fig.show()
