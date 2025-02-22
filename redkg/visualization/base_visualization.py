"""Base visualization module."""

from abc import ABC, abstractmethod
from typing import Any, Iterable

import matplotlib
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path
from scipy.spatial import ConvexHull

from redkg.visualization.config.parameters.defaults import Defaults
from redkg.visualization.contracts.draw_circle_edges_contract import DrawEdgesContract
from redkg.visualization.contracts.draw_vertex_contract import DrawVertexContract
from redkg.visualization.equations.calculate_common_tangent_radian import calculate_common_tangent_radian
from redkg.visualization.equations.calculate_polar_position import calculate_polar_position
from redkg.visualization.equations.calculate_rad_to_deg import calculate_rad_to_deg
from redkg.visualization.equations.calculate_radian_from_atan import calculate_radian_from_atan
from redkg.visualization.equations.calculate_vector_length import calculate_vector_length


class BaseVisualization(ABC):
    """Base visualization class with common functions."""

    contract = None

    @abstractmethod
    def draw(self):
        """Draw method to redefine."""
        raise NotImplementedError

    @abstractmethod
    def validate(self):
        """Validate."""
        raise NotImplementedError

    @staticmethod
    def draw_vertex(axes: Any, contract: DrawVertexContract) -> None:
        """Draw vertex based on contract DrawVertexContract.

        DrawVertexContract:
            - vertex_coordinates - Coordinates of the vertexes
            - vertex_label - Labels for vertexes
            - font_size - Font size base
            - font_family - Font family
            - vertex_size - Sizes for vertexes
            - vertex_color - Color for vertexes
            - vertex_line_width - Widths for vertexes
        """
        patches = []

        vertex_label: Iterable[str] = contract.vertex_label

        if contract.vertex_label is None:
            vertex_label = [""] * contract.vertex_coordinates.shape[0]  # noqa

        # Create vertexes
        for coordinates, label, size, width in zip(
            contract.vertex_coordinates.tolist(), vertex_label, contract.vertex_size, contract.vertex_line_width  # type: ignore[attr-defined] # noqa
        ):
            circle = Circle(coordinates, size)
            circle.lineWidth = width

            if label != "":
                # Get coordinates
                x, y = coordinates[0], coordinates[1]
                offset = 0, -1.3 * size
                x += offset[0]
                y += offset[1]
                # Apply to plot exes
                axes.text(
                    x, y, label, fontsize=contract.font_size, fontfamily=contract.font_family, ha="center", va="top"
                )

            patches.append(circle)

        # Make paths
        p = PatchCollection(patches, facecolors=contract.vertex_color, edgecolors="black")

        axes.add_collection(p)

    def draw_circle_edges(self, axes: Any, contract: DrawEdgesContract) -> None:
        """Draw circled edge based on contract DrawEdgesContract.

        DrawEdgesContract:
            - vertex_coordinates - Vertexes coordinates
            - vertex_size - Sizes for vertexes
            - edge_list - List of edges
            - edge_color - Colors for edges
            - edge_fill_color - Fill color for edges
            - edge_line_width - Width for edge lines
        """
        num_vertex = len(contract.vertex_coordinates)

        line_paths, arc_paths, vertices = self.hull_layout(
            num_vertex, contract.edge_list, contract.vertex_coordinates, contract.vertex_size
        )

        # For every edge line
        for edge_index, lines in enumerate(line_paths):
            path_data = []

            for line in lines:
                if len(line) == 0:
                    continue

                start_pos, end_pos = line

                path_data.append((Path.MOVETO, start_pos.tolist()))
                path_data.append((Path.LINETO, end_pos.tolist()))

            if len(list(zip(*path_data))) == 0:
                continue

            codes, vertexes = zip(*path_data)

            # Apply to plot
            axes.add_patch(
                PathPatch(
                    Path(vertexes, codes),
                    linewidth=contract.edge_line_width[edge_index],
                    facecolor=contract.edge_fill_color[edge_index],
                    edgecolor=contract.edge_color[edge_index],
                )
            )

        # For every arc
        for edge_index, arcs in enumerate(arc_paths):
            for arc in arcs:
                center, theta1, theta2, radius = arc

                # Apply to plot
                axes.add_patch(
                    matplotlib.patches.Arc(
                        (center[0], center[1]),
                        2 * radius,
                        2 * radius,
                        theta1=theta1,
                        theta2=theta2,
                        color=contract.edge_color[edge_index],
                        linewidth=contract.edge_line_width[edge_index],
                        edgecolor=contract.edge_color[edge_index],
                        facecolor=contract.edge_fill_color[edge_index],
                    )
                )

    @staticmethod
    def hull_layout(
        num_vertex: int,
        edge_list: Any,
        position: Any,
        vertex_size: Any,
        radius_increment: float = Defaults.radius_increment,
    ) -> tuple:  # noqa
        """
        Generate the layout for a graph with convex hulls for edges.

        This method computes the geometric layout for a graph, creating paths and arcs for edges
        based on the vertices' positions and sizes. It returns the paths and polygons for each edge.

        Args:
            num_vertex (int): Number of vertices in the graph.
            edge_list (Any): List of edges, where each edge is a list of vertex indices.
            position (Any): List of vertex positions in a 2D space.
            vertex_size (Any): Size of the vertices.
            radius_increment (float, optional): Factor to increase the vertex size for layout (default is `Defaults.radius_increment`).

        Returns:
            tuple: A tuple containing:
                - line_paths (list): List of line paths for the edges.
                - arc_paths (list): List of arc paths for the edges.
                - polygons_vertices_index (list): List of vertex indices for the polygons formed by edges.
        """
        # Make paths
        line_paths = [None] * len(edge_list)
        arc_paths = [None] * len(edge_list)

        # Make polygons
        polygons_vertices_index = []
        vertices_radius = np.array(vertex_size)
        vertices_increased_radius = vertices_radius * radius_increment
        vertices_radius += vertices_increased_radius

        # Define edge characteristics
        edge_degree = [len(e) for e in edge_list]
        edge_indexes = np.argsort(np.array(edge_degree))

        # For every edge index
        for edge_index in edge_indexes:
            edge = list(edge_list[edge_index])

            line_path_for_edges: list = []
            arc_path_for_edges: list = []

            if len(edge) == 1:
                arc_path_for_edges.append([position[edge[0]], 0, 360, vertices_radius[edge[0]]])

                vertices_radius[edge] += vertices_increased_radius[edge]

                line_paths[edge_index] = line_path_for_edges
                arc_paths[edge_index] = arc_path_for_edges

                continue

            pos_in_edge = position[edge]

            if len(edge) == 2:
                vertices_index = np.array((0, 1), dtype=np.int64)
            else:
                hull = ConvexHull(pos_in_edge)
                vertices_index = hull.vertices

            number_of_vertices = vertices_index.shape[0]

            vertices_index = np.append(vertices_index, vertices_index[0])  # close the loop

            thetas = []

            # For all vertexes
            for i in range(number_of_vertices):
                # draw lines
                i1 = edge[vertices_index[i]]
                i2 = edge[vertices_index[i + 1]]

                r1 = vertices_radius[i1]
                r2 = vertices_radius[i2]

                p1 = position[i1]
                p2 = position[i2]

                dp = p2 - p1
                dp_len = calculate_vector_length(dp)

                beta = calculate_radian_from_atan(dp[0], dp[1])
                alpha = calculate_common_tangent_radian(r1, r2, dp_len)

                theta = beta - alpha
                start_point = calculate_polar_position(r1, theta, p1)
                end_point = calculate_polar_position(r2, theta, p2)

                line_path_for_edges.append((start_point, end_point))
                thetas.append(theta)

            for i in range(number_of_vertices):
                # draw arcs
                theta_1 = thetas[i - 1]
                theta_2 = thetas[i]

                arc_center = position[edge[vertices_index[i]]]
                radius = vertices_radius[edge[vertices_index[i]]]

                theta_1, theta_2 = calculate_rad_to_deg(theta_1), calculate_rad_to_deg(theta_2)
                arc_path_for_edges.append((arc_center, theta_1, theta_2, radius))

            vertices_radius[edge] += vertices_increased_radius[edge]

            polygons_vertices_index.append(vertices_index.copy())

            # line_paths.append(line_path_for_e)
            # arc_paths.append(arc_path_for_e)
            line_paths[edge_index] = line_path_for_edges
            arc_paths[edge_index] = arc_path_for_edges

        return line_paths, arc_paths, polygons_vertices_index
