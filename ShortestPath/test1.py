inf = float("INF")

# 다익스트라 노드
datas = [
    [0, 1, inf, 1, inf, inf, inf, inf, inf, inf, inf, inf, inf],    # 1
    [1, 0, 1, inf, inf, inf, inf, inf, inf, inf, inf, inf, inf],    # 2
    [inf, 1, 0, inf, 1, inf, inf, inf, inf, inf, inf, inf, inf],    # 3
    [1, inf, inf, 0, inf, 1, inf, inf, inf, inf, inf, inf, inf],    # 4
    [inf, inf, 1, inf, 0, inf, inf, 1, inf, inf, inf, inf, inf],    # 5
    [inf, inf, inf, 1, inf, 0, 1, inf, 1, inf, inf, inf, inf],      # 6
    [inf, inf, inf, inf, inf, 1, 0, 1, inf, inf, inf, inf, inf],    # 7
    [inf, inf, inf, inf, 1, inf, 1, 0, inf, 1, inf, inf, inf],      # 8
    [inf, inf, inf, inf, inf, 1, inf, inf, 0, inf, 1, inf, inf],    # 9
    [inf, inf, inf, inf, inf, inf, inf,  1, inf, 0, inf, inf, 1],   # 10
    [inf, inf, inf, inf, inf, inf, inf, inf, 1, inf, 0, 1, inf],    # 11
    [inf, inf, inf, inf, inf, inf, inf, inf, inf, inf, 1, 0, 1],    # 12
    [inf, inf, inf, inf, inf, inf, inf, inf, inf, 1, inf, 1, 0]     # 13
]

# 에이스타 인접 리스트
graph = {
    1: {2: 1, 4: 1},
    2: {1: 1, 3: 1},
    3: {2: 1, 5: 1},
    4: {1: 1, 6: 1},
    5: {3: 1, 8: 1},
    6: {4: 1, 7: 1, 9: 1},
    7: {6: 1, 8: 1},
    8: {5: 1, 7: 1, 10: 1},
    9: {6: 1, 11: 1},
    10: {8: 1, 13: 1},
    11: {9: 1, 12: 1},
    12: {11: 1, 13: 1},
    13: {10: 1, 12: 1}
}

congestion = {
    1: {2: 1, 4: 1},
    2: {1: 1, 3: 1},
    3: {2: 1, 5: 1},
    4: {1: 1, 6: 1},
    5: {3: 1, 8: 1},
    6: {4: 1, 7: 1, 9: 1},
    7: {6: 1, 8: 1},
    8: {5: 1, 7: 1, 10: 1},
    9: {6: 1, 11: 1},
    10: {8: 1, 13: 1},
    11: {9: 1, 12: 1},
    12: {11: 1, 13: 1},
    13: {10: 1, 12: 1}
}

# # 노드의 혼잡도를 가정
# congestion = {
#     1: 1, 2: 1.5, 3: 2, 4: 1, 5: 1.8, 6: 1.2, 7: 1, 8: 1.6, 9: 2, 10: 1, 11: 1.1, 12: 1.4, 13: 1
# }

# def a_star_with_congestion(graph, start, goal, congestion):
#     pq = []
#     heapq.heappush(pq, (0, start))
#     came_from = {start: None}
#     cost_so_far = {start: 0}
    
#     while pq:
#         current = heapq.heappop(pq)[1]
        
#         if current == goal:
#             break
        
#         for next_node in graph[current]:
#             # 혼잡도를 가중치에 반영하여 비용 계산
#             congestion_factor = congestion.get(next_node, 1)  # 기본 혼잡도는 1
#             new_cost = cost_so_far[current] + graph[current][next_node] * congestion_factor
#             if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
#                 cost_so_far[next_node] = new_cost
#                 priority = new_cost + heuristic(goal, next_node)
#                 heapq.heappush(pq, (priority, next_node))
#                 came_from[next_node] = current
    
#     # 경로를 역추적하여 반환
#     current = goal
#     path = []
#     while current:
#         path.append(current)
#         current = came_from[current]
#     path.reverse()
    
#     return path

# # 혼잡도를 반영한 경로 탐색
# updated_path_with_congestion = a_star_with_congestion(graph, start_node, goal_node, congestion)

# # 결과 경로 출력
# print("혼잡도를 반영한 최적 경로:", updated_path_with_congestion)

import heapq

def heuristic(a, b):
    # 휴리스틱 함수: 여기서는 간단하게 두 노드 간 차이만 계산 (유클리드 거리는 필요하지 않음)
    # 예측용 함수로 모든 계산을 하기 전에 대략적인 예측을 하여 가능성 높은곳만 계산하도록 도와줌
    return 0

def a_star(graph, congestion, start, goal):
    """경로를 계산하여 반환하는 함수"""
    pq = []
    heapq.heappush(pq, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while pq:
        current = heapq.heappop(pq)[1]
        
        if current == goal:
            break
        
        for next_node in graph[current]:
            new_cost = cost_so_far[current] + graph[current][next_node] + congestion[current][next_node]
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(goal, next_node)
                heapq.heappush(pq, (priority, next_node))
                came_from[next_node] = current
    
    # 경로를 역추적하여 반환
    current = goal
    path = []
    while current:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    return path

# start와 goal을 정수로 설정
start = 12
goal = 6

# 최단 경로 탐색
path = a_star(graph, congestion,  start, goal)
print(f"최단 경로: {path}")
