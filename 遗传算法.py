import random
import math
import matplotlib.pyplot as plt
import numpy as np
# AGV初始坐标
agv_start = (190, 50)

# 目标点坐标（1-8号）
targets = [
    (70, 50),  # 1号目标点
    (110, 0),  # 2号
    (200, 0),  # 3号
    (250, 0),  # 4号
    (270, 50), # 5号
    (270, 100),# 6号
    (250, 160),# 7号
    (200, 160) # 8号
]
def calculate_distance(route):
    """计算路径总距离（包含从起点出发和返回起点）"""
    total = 0.0
    prev_x, prev_y = agv_start  # 固定起点
    for point_num in route:
        x, y = targets[point_num-1]
        total += math.hypot(x - prev_x, y - prev_y)
        prev_x, prev_y = x, y
    # 返回起点距离
    total += math.hypot(prev_x - agv_start[0], prev_y - agv_start[1])
    return total

def calculate_total_cost(route):
    """计算总成本：0.007*距离 + 0.18"""
    return 0.007 * calculate_distance(route) + 0.18

def create_population(n):
    """生成初始种群（每个个体为1-8的排列）"""
    return [random.sample(range(1, 9), 8) for _ in range(n)]

def fitness_evaluation(population):
    """计算适应度（总成本倒数）"""
    return [1/ calculate_distance(route) * 0.0024 for route in population]

def selection(population, fitness):
    """轮盘赌选择"""
    total = sum(fitness)
    probs = [f / total for f in fitness]

    # 构建累积概率
    for i in range(1, len(probs)):
        probs[i] += probs[i - 1]

    selected = []
    for _ in range(len(population)):
        rand = random.random()
        for i in range(len(probs)):
            if rand <= probs [i]:
                selected.append(population[i].copy())
                break
    return selected


def pmx_crossover(parent1, parent2):
    """部分映射交叉（处理1-8编号）"""
    size = len(parent1)
    cx1, cx2 = sorted(random.sample(range(size), 2))

    # 中间段交换
    child1 = parent1.copy()
    child2 = parent2.copy()
    child1[cx1: cx2 + 1], child2[cx1: cx2 + 1] = parent2[cx1:cx2 + 1], parent1[cx1:cx2 + 1]

    # 冲突修复
    for i in list(range(0, cx1)) + list(range(cx2 + 1, size)):
    # 处理child1
        while child1[i] in child1[cx1:cx2 + 1]:
            idx = parent2.index(child1[i])
            child1[i] = parent1[idx]
            # 处理child2
        while child2[i] in child2[cx1:cx2 + 1]:
                idx = parent1.index(child2[i])
                child2[i] = parent2[idx]
    return child1, child2

def mutate(route, mutation_rate):
    """交换变异（保持1-8编号）"""
    if random.random() < mutation_rate:
        i, j = random.sample(range(8), 2)
        route[i], route[j] = route[j], route[i]
    return route


# 算法参数
POP_SIZE = 100
GENERATIONS = 1000
MUTATION_RATE = 0.2
CROSSOVER_RATE = 0.6

# 初始化
population = create_population(POP_SIZE)
best_route = None
best_cost = float('inf')

# 适应度记录
avg_fitness = []
best_fitness = []

# 进化循环
for gen in range(GENERATIONS):
    # 评估适应度
    fitness = fitness_evaluation(population)

    # 记录统计量
    avg_fitness.append(np.mean(fitness))
    best_fitness.append(max(fitness))

    # 更新最优解
    current_best_route = population[fitness.index(max(fitness))]
    current_cost = calculate_total_cost(current_best_route)

    if current_cost < best_cost:
        best_cost = current_cost
        best_route = current_best_route.copy()

    # 选择
    selected = selection(population, fitness)

    # 交叉与变异
    new_pop = []
    for i in range(0, len(selected) - 1, 2):
        p1, p2 = selected[i], selected[i + 1]
        if random.random() < CROSSOVER_RATE:
            c1, c2 = pmx_crossover(p1, p2)
        else:
            c1, c2 = p1.copy(), p2.copy()
        new_pop.extend([mutate(c1, MUTATION_RATE), mutate(c2, MUTATION_RATE)])

    population = new_pop[:POP_SIZE]
# 结果输出
print(f"最优路径顺序（目标点编号）: {best_route}")
print(f"总成本: {best_cost:.2f}元")

# 详细路径分解
print("\n路径分解计算:")
prev_x, prev_y = agv_start
total_verify = 0
total_distance=0
for idx, point_num in enumerate(best_route, 1):
    x, y = targets[point_num - 1]
    distance = math.hypot(x - prev_x, y - prev_y)
    total_distance+=distance
    cost = 0.007 * distance + (0.18 / 9)  # 均摊惩罚成本到每个节点（包括返回起点）
    total_verify += cost
    print(f"段{idx}: ({prev_x},{prev_y}) → 目标点{point_num}({x},{y})")
    print(f" 距离: {distance:.2f}m | 成本: {cost:.2f}元")
    prev_x, prev_y = x, y
t=best_cost-total_verify
p=math.hypot(prev_x-agv_start[0],prev_y-agv_start[1])
total_distance+=p
print("返回起点费用为：{:.2f}元".format(t),"距离为：{:.2f}m".format(p))
print(f"验证总成本: {best_cost:.2f}元",f"总距离为：{total_distance:.2f}m")

# 可视化
plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows 系统常用字体
# plt.rcParams['font.sans-serif'] = ['Songti SC']  # macOS 系统常用字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示异常

# 进化过程可视化
plt.figure(figsize=(12, 6))
plt.plot(avg_fitness, label='平均适应度', alpha=0.7)
plt.plot(best_fitness, label='最佳适应度', linestyle='--')
plt.title('遗传算法优化过程')
plt.xlabel('迭代次数')
plt.ylabel('适应度')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# 路径可视化
plt.figure(figsize=(10, 8))
plt.scatter(agv_start[0], agv_start[1], s=200, marker='s', c='red', label='AGV起点')
colors = plt.cm.tab10.colors

# 绘制目标点
for i, (x, y) in enumerate(targets, 1):
    plt.scatter(x, y, s=100, color=colors[i % 10], label=f'目标点{i}')


# 绘制路径
prev = agv_start  # 初始起点
for point_num in best_route:
    x, y = targets[point_num - 1]
    plt.plot([prev, (x, y)], 'gray', alpha=0.5)  # 确保 prev 和 (x, y) 都是元组
    plt.annotate('', xy=(x, y), xytext=prev, arrowprops=dict(arrowstyle="->", lw=1.5))
    prev = (x, y)  # 更新 prev 为当前点的坐标

# 绘制返回起点的路径

plt.plot(prev, agv_start, 'gray', alpha=0.5)
plt.annotate('', xy=agv_start, xytext=prev, arrowprops=dict(arrowstyle="->", lw=1.5))

plt.title('最优路径可视化（包括返回起点）')
plt.xlabel('X坐标 (米)')
plt.ylabel('Y坐标 (米)')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()

