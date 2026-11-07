import os
import json
import heapq
import math
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
GRAPH_FILE = Path(os.environ.get("RAIL_GRAPH_FILE", str(BASE_DIR / "data/demo/rail_graph.json")))
STATIONS_FILE = Path(os.environ.get("STATION_GRAPH_FILE", str(BASE_DIR / "data/demo/station_graph.json")))


print("Načítám železniční data...")

start_time = time.perf_counter()


with GRAPH_FILE.open(
    "r",
    encoding="utf-8"
) as file:
    graph = json.load(file)


with STATIONS_FILE.open(
    "r",
    encoding="utf-8"
) as file:
    station_data = json.load(file)


nodes = graph["nodes"]
edges = graph["edges"]
adjacency = graph["adjacency"]

stations = station_data["stations"]


# --------------------------------------------------
# Vyhledávání stanic
# --------------------------------------------------

station_lookup = {}

for station in stations:

    name = station.get("name")

    if not name:
        continue

    station_lookup.setdefault(
        name.casefold(),
        []
    ).append(station)


def find_station(name):

    results = station_lookup.get(
        name.strip().casefold(),
        []
    )

    if not results:
        return None

    return results[0]


# --------------------------------------------------
# Délka hrany
# --------------------------------------------------

def edge_length(edge_id):

    edge = edges[int(edge_id)]

    if isinstance(edge, list):
        return float(edge[2])

    return float(edge["length_km"])


def edge_coordinates(edge_id):

    edge = edges[int(edge_id)]

    if isinstance(edge, list):
        start_node = int(edge[0])
        end_node = int(edge[1])
    else:
        start_node = int(edge["start"])
        end_node = int(edge["end"])

    start_lon, start_lat = nodes[start_node]
    end_lon, end_lat = nodes[end_node]

    # Leaflet používá [lat, lon]
    return [
        [start_lat, start_lon],
        [end_lat, end_lon]
    ]


# --------------------------------------------------
# Dijkstra
# --------------------------------------------------

def dijkstra(start_node, end_node):

    start_node = int(start_node)
    end_node = int(end_node)

    distances = {
        start_node: 0.0
    }

    previous = {}
    previous_edge = {}

    queue = [
        (0.0, start_node)
    ]

    while queue:

        current_distance, node = heapq.heappop(
            queue
        )

        if current_distance != distances.get(node):
            continue

        if node == end_node:
            break

        for neighbor, edge_id in adjacency[node]:

            neighbor = int(neighbor)

            new_distance = (
                current_distance
                + edge_length(edge_id)
            )

            if new_distance < distances.get(
                neighbor,
                math.inf
            ):

                distances[neighbor] = new_distance

                previous[neighbor] = node
                previous_edge[neighbor] = edge_id

                heapq.heappush(
                    queue,
                    (
                        new_distance,
                        neighbor
                    )
                )

    if end_node not in distances:
        return None

    path = [end_node]
    path_edges = []

    while path[-1] != start_node:

        current_node = path[-1]

        path_edges.append(
            int(previous_edge[current_node])
        )

        path.append(
            previous[current_node]
        )

    path.reverse()
    path_edges.reverse()

    return {
        "distance_km": distances[end_node],
        "nodes": path,
        "edge_ids": path_edges
    }


# --------------------------------------------------
# Trasa mezi stanicemi
# --------------------------------------------------

def find_route(start_name, end_name):

    start_station = find_station(start_name)
    end_station = find_station(end_name)

    if start_station is None:
        return {
            "error":
                f"Stanice nenalezena: {start_name}"
        }

    if end_station is None:
        return {
            "error":
                f"Stanice nenalezena: {end_name}"
        }

    result = dijkstra(
        start_station["rail_node"],
        end_station["rail_node"]
    )

    if result is None:
        return {
            "error":
                "Mezi stanicemi nebyla nalezena trasa."
        }

    coordinates = []

    for node_id in result["nodes"]:

        lon, lat = nodes[node_id]

        # Leaflet používá [lat, lon]
        coordinates.append(
            [lat, lon]
        )

    return {
        "start": start_station["name"],
        "end": end_station["name"],
        "distance_km": round(
            result["distance_km"],
            3
        ),
        "coordinates": coordinates,
        "node_count": len(result["nodes"]),
        "edge_ids": result["edge_ids"],
        "edge_count": len(result["edge_ids"])
    }

# --------------------------------------------------
# Trasa přes více stanic
# --------------------------------------------------

def find_route_via(station_names):

    # Potřebujeme minimálně start a cíl
    if not station_names or len(station_names) < 2:
        return {
            "error":
                "Je nutné zadat alespoň výchozí a cílovou stanici."
        }

    # Odstraníme prázdné názvy
    station_names = [
        name.strip()
        for name in station_names
        if name and name.strip()
    ]

    if len(station_names) < 2:
        return {
            "error":
                "Je nutné zadat alespoň výchozí a cílovou stanici."
        }

    total_distance = 0.0

    all_coordinates = []

    all_edge_ids = []

    segments = []


    # ----------------------------------------------
    # Výpočet jednotlivých úseků
    # ----------------------------------------------

    for index in range(len(station_names) - 1):

        start_name = station_names[index]
        end_name = station_names[index + 1]

        result = find_route(
            start_name,
            end_name
        )


        if "error" in result:

            return {
                "error":
                    f"{start_name} → {end_name}: "
                    f"{result['error']}"
            }


        total_distance += result["distance_km"]

        all_edge_ids.extend(
            result["edge_ids"]
        )


        # U prvního úseku vezmeme všechny body.
        # U dalších vynecháme první bod,
        # protože je totožný s posledním bodem
        # předchozího úseku.

        if not all_coordinates:

            all_coordinates.extend(
                result["coordinates"]
            )

        else:

            all_coordinates.extend(
                result["coordinates"][1:]
            )


        segments.append({
            "start": result["start"],
            "end": result["end"],
            "distance_km":
                result["distance_km"],
            "node_count":
                result["node_count"],
            "edge_count":
                result["edge_count"]
        })


    return {
        "start": station_names[0],
        "end": station_names[-1],
        "via": station_names[1:-1],

        "distance_km": round(
            total_distance,
            3
        ),

        "coordinates":
            all_coordinates,

        "edge_ids":
            all_edge_ids,

        "edge_count":
            len(all_edge_ids),

        "segments":
            segments,

        "segment_count":
            len(segments),

        "point_count":
            len(all_coordinates)
    }
load_time = time.perf_counter() - start_time

print(
    f"Železniční data načtena za "
    f"{load_time:.2f} s."
)

print(
    f"{len(nodes):,} uzlů, "
    f"{len(edges):,} hran, "
    f"{len(stations):,} stanic."
)