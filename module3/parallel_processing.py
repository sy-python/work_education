import concurrent.futures
import json
import multiprocessing
import random
import time
from typing import Callable

import pandas


def generate_data(n: int) -> list[int]:
    return [random.randint(0, 1000) for _ in range(n)]


def process_number(n: int) -> int:
    f = 1
    for i in range(1, n + 1):
        f *= i
    return f


def thread_pool(data: list[int]) -> list[int]:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(process_number, data)
    return list(results)


def process_pool(data: list[int]) -> list[int]:
    with multiprocessing.Pool() as pool:
        results = pool.map(process_number, data)
    return list(results)


def worker(
    input_queue: multiprocessing.Queue,
    output_queue: multiprocessing.Queue,
):
    while True:
        index, number = input_queue.get()
        if index == -1:
            break
        result = process_number(number)
        output_queue.put((index, result))


def individual_processes(data: list[int]) -> list[int]:
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()

    processes = [
        multiprocessing.Process(target=worker, args=(input_queue, output_queue))
        for _ in range(multiprocessing.cpu_count())
    ]

    for process in processes:
        process.start()

    for index, number in enumerate(data):
        input_queue.put((index, number))

    for _ in processes:
        input_queue.put((-1, -1))

    results = [None for _ in data]
    for _ in data:
        index, result = output_queue.get()
        results[index] = result

    for process in processes:
        process.join()

    return results


def non_concurrent(data: list[int]) -> list[int]:
    return [process_number(number) for number in data]


def measure_time(
    data: list[int], func: Callable[[list[int]], list[int]]
) -> tuple[list[int], float]:
    start = time.perf_counter()
    results = func(data)
    end = time.perf_counter()
    return results, end - start


def main() -> None:
    data = generate_data(10_000)

    results_thread_pool, time_thread_pool = measure_time(data, thread_pool)
    results_process_pool, time_process_pool = measure_time(data, process_pool)
    results_individual_processes, time_individual_processes = measure_time(
        data, individual_processes
    )
    results_non_concurrent, time_non_concurrent = measure_time(data, non_concurrent)

    assert results_thread_pool == results_process_pool
    assert results_thread_pool == results_individual_processes
    assert results_thread_pool == results_non_concurrent

    results_json = {
        "Пул потоков": time_thread_pool,
        "Пул процессов": time_process_pool,
        "Отдельные процессы": time_individual_processes,
        "Однопоточный": time_non_concurrent,
    }

    frame = pandas.DataFrame(list(results_json.items()), columns=["Метод", "Время (с)"])
    print(frame)

    with open("results.json", "w") as f:
        json.dump(results_json, f)


if __name__ == "__main__":
    main()
