from torch import tensor

from redkg.visualization.config.parameters.generator_methods import GeneratorMethods
from redkg.visualization.contracts.hypergraph_contract import HypergraphContract
from redkg.visualization.contracts.hypergraph_visualization_contract import HypergraphVisualizationContract
from redkg.visualization.hypergraph_visualization import HypergraphVisualizer

from redkg.visualization.data_generation.hypergraph_generator import HypergraphGenerator


VERTEX_NUM = 500
EDGE_NUM = 300

generator = HypergraphGenerator(vertex_num=VERTEX_NUM, edge_num=EDGE_NUM, generation_method=GeneratorMethods.uniform)
generated_data = generator()

generated_edge_weights = [1.0 for _ in range(len(generated_data))]


graph_contract: HypergraphContract = HypergraphContract(
    vertex_num=VERTEX_NUM,
    edge_list=(  # noqa
        generated_data,
        generated_edge_weights
    ),
    edge_num=EDGE_NUM,
    edge_weights=tensor(  # noqa
        generated_edge_weights * 2
    ),
)
vis_contract: HypergraphVisualizationContract = HypergraphVisualizationContract(graph=graph_contract)

vis: HypergraphVisualizer = HypergraphVisualizer(vis_contract)
fig = vis.draw()
fig.show()
