import time
import asyncio
import aiohttp
import statistics
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Define base URLs for original and Cythonized versions
BASE_URL_ORIGINAL = "http://localhost:8000/api/"
BASE_URL_CYTHON = "http://localhost:8001/api/"

# Define endpoints to test
ENDPOINTS = [
    {"path": "employees/", "method": "GET"},
    {"path": "projects/", "method": "GET"},
    {"path": "tasks/", "method": "GET"},
    {"path": "expenses/", "method": "GET"},
    {"path": "employees/", "method": "POST"},
    {"path": "projects/", "method": "POST"},
    {"path": "tasks/", "method": "POST"},
    {"path": "expenses/", "method": "POST"},
]

# Define heavy operations
HEAVY_OPERATIONS = [
    {"path": "employees/top_performers/", "method": "GET"},
    {"path": "projects/budget_analysis/", "method": "GET"},
    {"path": "tasks/overdue_analysis/", "method": "GET"},
    {"path": "expenses/category_analysis/", "method": "GET"},
]

# Test settings
CONCURRENT_USERS = 100
TEST_DURATION = .1  # seconds

async def make_request(session, url, method):
    start_time = time.time()
    try:
        if method == "GET":
            async with session.get(url) as response:
                await response.text()
        elif method == "POST":
            async with session.post(url, json={"data": "test"}) as response:
                await response.text()
        return time.time() - start_time, response.status
    except Exception as e:
        return None, str(e)

async def user_behavior(session, base_url):
    while True:
        for endpoint in ENDPOINTS + HEAVY_OPERATIONS:
            url = base_url + endpoint["path"]
            yield await make_request(session, url, endpoint["method"])

async def load_test(base_url, duration, concurrent_users):
    results = []
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [user_behavior(session, base_url) for _ in range(concurrent_users)]
        while time.time() - start_time < duration:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                results.extend(task.result())
                tasks.remove(task)
                tasks.add(asyncio.create_task(user_behavior(session, base_url)))
    return results

def run_test(base_url):
    return asyncio.run(load_test(base_url, TEST_DURATION, CONCURRENT_USERS))

def analyze_results(results):
    response_times = [r[0] for r in results if r[0] is not None]
    status_codes = [r[1] for r in results]
    
    return {
        "total_requests": len(results),
        "successful_requests": status_codes.count(200),
        "failed_requests": len(results) - status_codes.count(200),
        "avg_response_time": statistics.mean(response_times),
        "median_response_time": statistics.median(response_times),
        "min_response_time": min(response_times),
        "max_response_time": max(response_times),
        "requests_per_second": len(results) / TEST_DURATION
    }

def create_comparison_chart(original_analysis, cython_analysis):
    labels = ['Avg Response Time', 'Median Response Time', 'Min Response Time', 'Max Response Time']
    original_data = [original_analysis[f"{label.lower().replace(' ', '_')}"] for label in labels]
    cython_data = [cython_analysis[f"{label.lower().replace(' ', '_')}"] for label in labels]

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - width/2 for i in x], original_data, width, label='Original', color='blue', alpha=0.7)
    ax.bar([i + width/2 for i in x], cython_data, width, label='Cython', color='green', alpha=0.7)

    ax.set_ylabel('Time (seconds)')
    ax.set_title('Performance Comparison: Original vs Cython')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    plt.tight_layout()
    
    # Create charts directory if it doesn't exist
    os.makedirs('charts', exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'charts/performance_comparison_{timestamp}.png'
    plt.savefig(filename)
    print(f"Comparison chart saved as {filename}")

def main():
    print("Starting performance test...")
    print(f"Testing {CONCURRENT_USERS} concurrent users for {TEST_DURATION} seconds")
    print(f"Endpoints being tested: {len(ENDPOINTS) + len(HEAVY_OPERATIONS)}")

    with ProcessPoolExecutor(max_workers=2) as executor:
        future_original = executor.submit(run_test, BASE_URL_ORIGINAL)
        future_cython = executor.submit(run_test, BASE_URL_CYTHON)

        results_original = future_original.result()
        results_cython = future_cython.result()

    analysis_original = analyze_results(results_original)
    analysis_cython = analyze_results(results_cython)

    print("\nResults for Original Version:")
    for key, value in analysis_original.items():
        print(f"{key}: {value}")

    print("\nResults for Cython Version:")
    for key, value in analysis_cython.items():
        print(f"{key}: {value}")

    improvement = (analysis_original['avg_response_time'] - analysis_cython['avg_response_time']) / analysis_original['avg_response_time'] * 100
    print(f"\nPerformance improvement: {improvement:.2f}%")

    create_comparison_chart(analysis_original, analysis_cython)

if __name__ == "__main__":
    main()