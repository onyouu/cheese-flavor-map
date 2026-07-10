import json
import math
import copy

INPUT_FILE = "umap_coordinates.json"
OUTPUT_FILE = "umap_coordinates_relaxed.json"

def get_font_size(sv):
    if sv and sv > 0:
        return max(9, min(22, 10 + (sv / 100) * 12))
    return 9

def main():
    print(f"Loading {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        umap_data = json.load(f)
        
    print("Loading all_cheeses_with_search.json...")
    with open("all_cheeses_with_search.json", "r", encoding="utf-8") as f:
        cheeses_data = json.load(f)
        
    search_volumes = {c['name']: c.get('search_volume', 0) for c in cheeses_data}
    
    nodes = []
    
    xs = [d['x'] for d in umap_data.values()]
    ys = [d['y'] for d in umap_data.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    def scale_x(x):
        return -4000 + (x - min_x) * (8000 / (max_x - min_x)) if max_x > min_x else 0
    def scale_y(y):
        return 4000 + (y - min_y) * (-8000 / (max_y - min_y)) if max_y > min_y else 0
    
    def unscale_x(sx):
        return min_x + (sx - (-4000)) * ((max_x - min_x) / 8000)
    def unscale_y(sy):
        return min_y + (sy - 4000) * ((max_y - min_y) / -8000)
        
    for name, d in umap_data.items():
        sv = search_volumes.get(name, 0)
        size = get_font_size(sv)
        
        width = len(name) * size * 0.4
        height = size * 1.2
        radius = math.sqrt((width/2)**2 + (height/2)**2) * 1.5 # 50% padding for better separation
        
        nodes.append({
            "name": name,
            "orig_x": scale_x(d['x']),
            "orig_y": scale_y(d['y']),
            "x": scale_x(d['x']),
            "y": scale_y(d['y']),
            "vx": 0.0,
            "vy": 0.0,
            "radius": radius
        })
    
    print("Starting simulation (150 iterations)...")
    num_iterations = 150
    alpha = 1.0
    alpha_decay = 1 - pow(0.001, 1/num_iterations)
    
    for iter_idx in range(num_iterations):
        if iter_idx % 25 == 0:
            print(f"Iteration {iter_idx}/{num_iterations}")
            
        # Collision Force
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1 = nodes[i]
                n2 = nodes[j]
                dx = n2['x'] - n1['x']
                dy = n2['y'] - n1['y']
                dist_sq = dx*dx + dy*dy
                rad_sum = n1['radius'] + n2['radius']
                if dist_sq < rad_sum*rad_sum and dist_sq > 0:
                    dist = math.sqrt(dist_sq)
                    overlap = (rad_sum - dist) / dist
                    # Weight by radius so smaller nodes move more
                    total_rad = rad_sum
                    w1 = n2['radius'] / total_rad
                    w2 = n1['radius'] / total_rad
                    
                    fx = dx * overlap * alpha * 0.5
                    fy = dy * overlap * alpha * 0.5
                    
                    n1['vx'] -= fx * w1
                    n1['vy'] -= fy * w1
                    n2['vx'] += fx * w2
                    n2['vy'] += fy * w2
                    
        # Anchor Force (pull back to original position to preserve clusters)
        for n in nodes:
            dx = n['orig_x'] - n['x']
            dy = n['orig_y'] - n['y']
            n['vx'] += dx * 0.05 * alpha
            n['vy'] += dy * 0.05 * alpha
            
        # Update positions
        for n in nodes:
            n['x'] += n['vx']
            n['y'] += n['vy']
            # Apply friction
            n['vx'] *= 0.6
            n['vy'] *= 0.6
            
        alpha *= (1 - alpha_decay)
        
    print("Simulation complete. Formatting data...")
    # Update data with unscaled coordinates
    for n in nodes:
        name = n['name']
        umap_data[name]['x'] = unscale_x(n['x'])
        umap_data[name]['y'] = unscale_y(n['y'])
        
    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(umap_data, f, ensure_ascii=False, indent=2)
        
    print("Done!")

if __name__ == "__main__":
    main()
