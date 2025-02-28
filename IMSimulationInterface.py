import numpy as np

from intersection_control.interfaces import IMEnvironmentInterface
import traci
import sumolib


class IMSimulationInterface(IMEnvironmentInterface):
    def __init__(self, intersection_id):
        self.intersection_id = intersection_id
        self.net = sumolib.net.readNet("network/intersection.net.xml", withInternal=True)
        self.routes = list(sumolib.xml.parse_fast("network/intersection.rou.xml", 'route', ['id', 'edges']))

    def get_position(self) -> (float, float):
        return traci.junction.getPosition(self.intersection_id)

    def get_current_time(self):
        return traci.simulation.getTime()

    def get_width(self) -> float:
        shape = traci.junction.getShape(self.intersection_id)
        xs = [x for (x, _) in shape]
        return max(xs) - min(xs)

    def get_height(self):
        shape = traci.junction.getShape(self.intersection_id)
        ys = [y for (y, _) in shape]
        return max(ys) - min(ys)

    def get_trajectories(self):
        internal_edges = [edge for edge in self.net.getEdges() if edge.getFunction() == "internal"]
        return {self.get_route_through_edge(edge): [np.array(point) for point in edge.getShape()] for edge in internal_edges}

    def get_route_through_edge(self, edge):
        for route in self.routes:
            edges = route.edges.split()
            inner_connection = self.net.getEdge(edges[0]).getConnections(self.net.getEdge(edges[1]))[0]
            if self.net.getLane(inner_connection.getViaLaneID()).getEdge().getID() == edge.getID():
                return route.id
        return None


