from typing import Any, Dict
from datetime import datetime, timedelta

def handler(event: Dict, context: object) -> Dict[str, Any]:
    def parse_timestamp(ts_str: str) -> datetime:
        return datetime.fromisoformat(ts_str)

    if not hasattr(context, 'env'):
        context.env = {}

    if "cpu_hist" not in context.env:
        context.env["cpu_hist"] = {}

    current_time = parse_timestamp(event["timestamp"])

    cpu_usage_map = {}
    for k, v in event.items():
        if k.startswith("cpu_percent-"):
            cpu_index = k.split("-")[1]
            cpu_usage_map[cpu_index] = float(v)

    # Step 1: Calculate the percentage of outgoing bytes.
    net_bytes_sent = float(event.get("net_io_counters_eth0-bytes_sent", 0.0))
    net_bytes_recv = float(event.get("net_io_counters_eth0-bytes_recv", 0.0))
    net_total = net_bytes_sent + net_bytes_recv
    percent_network_egress = 0.0
    if net_total != 0:
        percent_network_egress = (net_bytes_sent / net_total) * 100.0

    # Step 2: Calculate the percentage of memory used for caching (cached + buffers).
    vm_cached = float(event.get("virtual_memory-cached", 0.0))
    vm_buffers = float(event.get("virtual_memory-buffers", 0.0))
    vm_total = float(event.get("virtual_memory-total", 0.0))
    percent_memory_cache = 0.0
    if vm_total != 0:
        percent_memory_cache = ((vm_cached + vm_buffers) / vm_total) * 100.0

    # Step 3: Compute the moving average
    now = current_time
    sixty_seconds_ago = now - timedelta(seconds=60)

    results = {
        "percent-network-egress": percent_network_egress,
        "percent-memory-caching": percent_memory_cache,
        "timestamp": now.isoformat()
    }

    for cpu_index, usage_value in cpu_usage_map.items():
        if cpu_index not in context.env["cpu_hist"]:
            context.env["cpu_hist"][cpu_index] = []

        context.env["cpu_hist"][cpu_index].append((now, usage_value))

        # Remove data older than 60 seconds.
        history = context.env["cpu_hist"][cpu_index]
        context.env["cpu_hist"][cpu_index] = [
            (t, val) for (t, val) in history if t >= sixty_seconds_ago
        ]

        # Compute average CPU usage for the last 60 seconds.
        recent_values = [val for (t, val) in context.env["cpu_hist"][cpu_index]]
        avg_cpu_usage = sum(recent_values) / len(recent_values) if recent_values else 0.0

        results[f"avg-util-cpu{cpu_index}-60sec"] = avg_cpu_usage

    print(f"{now}\tFinal env:")
    #print(context.env)

    return results

