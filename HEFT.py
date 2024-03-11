# tasks = [1, 2, 3, 4, 5, 6]
# dependencies = {2: [1], 4: [2, 3], 5: [3], 6: [4]}
# times = {1: 1, 2: 2, 3: 4, 4: 1, 5: 2, 6: 3}

tasks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
dependencies = {2: [1], 4: [2, 3], 5: [3], 6: [4], 8: [5, 6], 9: [7, 8], 10: [
    9], 11: [10], 12: [10], 13: [11, 12], 14: [13], 15: [13], 16: [14, 15]}
times = {1: 2, 2: 3, 3: 4, 4: 2, 5: 3, 6: 1, 7: 2, 8: 3,
         9: 4, 10: 2, 11: 3, 12: 2, 13: 4, 14: 2, 15: 3, 16: 1}


def EFT(task):
    if task not in dependencies:
        t = times[task]
    else:
        max_EFT_parent = max(EFT(parent) for parent in dependencies[task])
        t = max_EFT_parent + times[task]

    return t


sorted_tasks = sorted(tasks, key=EFT)
makespan = EFT(sorted_tasks[-1])

print(sorted_tasks, makespan)
