import numpy as np
from starter import ZONES, TIME_BLOCKS, COSTS, PROMISE, delivery_times

def calculate_late_percentage(zone, time_block, promise=PROMISE, seed=42):
    zones = ZONES if zone == "all" else [zone]
    time_blocks = TIME_BLOCKS if time_block == "all" else [time_block]
    
    total_orders = 0
    total_late = 0
    
    for z in zones:
        for tb in time_blocks:
            times = delivery_times(z, tb, promise, seed=seed)
            total_orders += len(times)
            total_late += np.sum(times > promise)
            
    if total_orders == 0:
        return 0.0
    return float((total_late / total_orders) * 100)


def calculate_average_delivery_time(zone, time_block, promise=PROMISE, seed=42):
    zones = ZONES if zone == "all" else [zone]
    time_blocks = TIME_BLOCKS if time_block == "all" else [time_block]
    
    all_times = []
    for z in zones:
        for tb in time_blocks:
            times = delivery_times(z, tb, promise, seed=seed)
            if len(times) > 0:
                all_times.append(times)
                
    if not all_times:
        return 0.0
    combined = np.concatenate(all_times)
    return float(np.mean(combined))


def calculate_late_cost_per_order(costs=COSTS):
    refund = costs["refund"]
    churn_loss = costs["churn_orders"] * costs["margin"]
    return float(refund + churn_loss)


def choose_best_promise(zone, time_block, promises, costs=COSTS, seed=42):
    cost_per_late = calculate_late_cost_per_order(costs)
    margin = costs["margin"]
    
    best_promise = None
    best_net_profit = float("-inf")
    results = []
    
    for p in promises:
        times = delivery_times(zone, time_block, p, seed=seed)
        n_orders = len(times)
        if n_orders == 0:
            net_profit = 0.0
            late_rate = 0.0
            n_late = 0
        else:
            n_late = int(np.sum(times > p))
            late_rate = float((n_late / n_orders) * 100)
            gross_profit = n_orders * margin
            late_cost = n_late * cost_per_late
            net_profit = float(gross_profit - late_cost)
            
        results.append({
            "promise": p,
            "orders": n_orders,
            "late_orders": n_late,
            "late_rate": late_rate,
            "net_profit": net_profit
        })
        
        if net_profit > best_net_profit:
            best_net_profit = net_profit
            best_promise = p
            
    return {
        "best_promise": best_promise,
        "best_net_profit": best_net_profit,
        "grid_results": results
    }

if __name__ == "__main__":
    print("Testing Part I (a)...")
    print("Far West, Fri/Sat eve:", round(calculate_late_percentage("Far West", "Fri/Sat eve", 45), 2))
    print("Far West, all:", round(calculate_late_percentage("Far West", "all", 45), 2))
    print("all, Lunch:", round(calculate_late_percentage("all", "Lunch", 45), 2))
    print("all, all:", round(calculate_late_percentage("all", "all", 45), 2))

    print("\nTesting Part I (b) Rankings by Late Rate...")
    late_ranks = []
    for z in ZONES:
        for tb in TIME_BLOCKS:
            lr = calculate_late_percentage(z, tb, 45)
            late_ranks.append((z, tb, lr))
    late_ranks.sort(key=lambda x: x[2], reverse=True)
    for r in late_ranks:
        print(f"{r[0]:<10} {r[1]:<15} {r[2]:.2f}%")

    print("\nTesting Part I (c)...")
    print("Far West, Fri/Sat eve:", round(calculate_average_delivery_time("Far West", "Fri/Sat eve", 45), 2))
    print("Far West, all:", round(calculate_average_delivery_time("Far West", "all", 45), 2))
    print("all, Lunch:", round(calculate_average_delivery_time("all", "Lunch", 45), 2))
    print("all, all:", round(calculate_average_delivery_time("all", "all", 45), 2))

    print("\nTesting Part I (d) Rankings by Avg Delivery Time...")
    time_ranks = []
    for z in ZONES:
        for tb in TIME_BLOCKS:
            dt = calculate_average_delivery_time(z, tb, 45)
            time_ranks.append((z, tb, dt))
    time_ranks.sort(key=lambda x: x[2], reverse=True)
    for r in time_ranks:
        print(f"{r[0]:<10} {r[1]:<15} {r[2]:.2f} mins")

    print("\nTesting Part II (a) Late Cost...")
    cost_per_late = calculate_late_cost_per_order()
    print("Cost per late order:", cost_per_late)

    print("\nTesting Part II (b) Best Promise...")
    promises_to_test = list(range(20, 65, 5))
    res = choose_best_promise("Far West", "Fri/Sat eve", promises_to_test)
    print("Best promise for Far West, Fri/Sat eve:", res["best_promise"], "Net profit:", round(res["best_net_profit"], 2))
    for r in res["grid_results"]:
        print(f"Promise: {r['promise']:2d} min | Orders: {r['orders']:3d} | Late: {r['late_orders']:3d} ({r['late_rate']:5.1f}%) | Net Profit: ${r['net_profit']:7.2f}")
