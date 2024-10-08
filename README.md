# Xelify: A Task Scheduling Algorithm Framework

## Overview

**Xelify** is a task scheduling framework designed to solve complex scheduling problems by optimally assigning tasks to available workers. The framework employs various scheduling algorithms that aim to meet task requirements while considering the capacities and attributes of workers. 

This repository includes:

- **Scheduling Algorithms:** The core algorithms in the `xelify.py` file solve the task scheduling problem by considering both workers' abilities and tasks' requirements.
- **Example Implementation:** A Jupyter notebook demonstrating how to apply the algorithms to a practical scheduling scenario using sample data.
- **Sample Data:** Two CSV files representing the tasks to be scheduled and the available workers.

## The Scheduling Problem

The scheduling problem addressed by Xelify involves assigning a set of tasks to a group of workers in an efficient way. The goal is to maximize the productivity of the workforce while satisfying task-specific constraints such as:

1. **Skill Requirements:** Tasks may require certain skills that only some workers possess.
2. **Availability:** Workers might only be available at specific times, which should match the time constraints of the tasks.
3. **Capacity and Load:** Workers may have a maximum number of tasks they can handle at once, and the algorithm must distribute tasks accordingly to avoid overload.
4. **Task Deadlines:** Tasks may have deadlines, and they must be completed within a specified time frame.

The objective is to balance these constraints, ensuring that all tasks are completed by qualified workers without exceeding their workload.

## Data Explanation

The framework uses two main datasets:

1. **Worker Data** (`df_hum.csv`): Information on the available workers, their availability, and the equipment they operate.
2. **Task Data** (`df_toy.csv`): Details about tasks to be completed, including required resources and processing times.

### Worker Data

The worker data provides a schedule for each worker from Monday to Friday. Each worker has multiple time slots in which they are available to work, and they also have access to certain equipment necessary to complete tasks. The key fields are:

- **Manutentionaire (Worker ID):** A unique identifier for each worker.
- **Day-wise Time Slots:** For each day of the week (Monday to Friday), a list of available time intervals is provided, where each interval is a tuple indicating the start and end times of availability. Example: `[[7.0, 12.0], [13.0, 15.0]]` means the worker is available from 7:00 to 12:00 and from 13:00 to 15:00 on that day.
- **Equipement (Equipment):** An array of integers representing whether the worker has access to certain equipment. The equipment may represent tools or machinery needed for specific tasks, e.g., `[1, 0, 1]` indicates that the worker has access to the first and third pieces of equipment but not the second.

#### Worker Data Example:
| Manutentionaire | Lundi                 | Mardi                 | Mercredi              | Jeudi                 | Vendredi              | Equipement  |
|-----------------|-----------------------|-----------------------|-----------------------|-----------------------|-----------------------|-------------|
| 1               | [[7.0, 10.0], [11.0, 12.0]] | [[7.0, 12.0]]          | [[7.0, 12.0]]          | [[7.0, 12.0]]          | [[7.0, 12.0]]          | [1, 0, 1]   |
| 2               | [[7.0, 12.0], [13.0, 15.5]] | [[7.0, 10.0], [13.0, 15.5]] | [[7.0, 12.0]]          | [[7.0, 12.0]]          | [[7.0, 12.0]]          | [1, 0, 1]   |

### Task Data

The task data contains the details of the tasks that need to be scheduled. Each task has a specific processing time, quantity of items, and equipment requirements. The key fields include:

- **ID:** A unique identifier for each task.
- **Date de Creation (Creation Date):** The date and time when the task was created.
- **Societe (Company):** The company requesting the task.
- **Transporteur (Transporter):** The service transporting the goods (e.g., UPS, Colissimo).
- **Quantite Articles (Quantity of Articles):** The number of articles or items to be processed.
- **Temps de Passage (Processing Time):** The time required to process the articles (in seconds).
- **Temps Init (Initial Time):** The base time required before handling the quantity of articles (in hours).
- **Temps Quantite (Time per Quantity):** The additional time needed per unit of quantity (in hours).
- **Temps Total (Total Time):** The total processing time required for the task, which is calculated as the sum of the initial time and the time required per quantity.
- **Equipement (Equipment Requirements):** An array indicating which equipment is required to complete the task (similar to the worker's equipment).

#### Task Data Example:
| ID  | Date de Creation | Societe | Transporteur         | Quantite Articles | Temps de Passage | Temps Init | Temps Quantite | Temps Total | Equipement  |
|-----|------------------|---------|----------------------|-------------------|------------------|------------|----------------|-------------|-------------|
| 0   | 9/1/22 18:53     | S1      | UPS                  | 10                | 360              | 3          | 10             | 13          | [0, 0, 0]   |
| 1   | 9/1/22 18:53     | S1      | UPS                  | 12                | 360              | 3          | 12             | 15          | [0, 0, 0]   |
| 2   | 9/1/22 19:12     | S2      | Colissimo Domicile    | 1                 | 450              | 6          | 1              | 7           | [1, 0, 0]   |

## Solution Approach

The scheduling algorithms implemented in `xelify.py` aim to assign tasks to workers using a modified version of the Jackson algorithm.

## Jackson_bw Algorithm Overview

The `Jackson_bw` algorithm schedules tasks by assigning them to workers and machines while considering task deadlines, worker availability, and machine requirements. It operates iteratively, aiming to find the best possible scheduling arrangement for each task.

### Input Parameters

- `num_tareas`: Number of tasks.
- `num_maquinas`: Number of machines.
- `num_trabajadores`: Number of workers.
- `tiempos_procesamiento`: List of processing times for each task.
- `habilidades_trabajadores`: Matrix indicating which workers can operate specific machines.
- `horarios_trabajadores`: Worker availability in time intervals.
- `deadlines`: Task deadlines.
- `machine_required`: List of machines required for each task.

### Process Summary

1. **Task Prioritization:** Tasks are ordered by deadlines.
2. **Machine and Worker Assignment:** The algorithm checks worker skills and availability, and verifies if the required machines are available during the worker's free time. The task is then assigned if all conditions are met.
3. **Task Without Machines:** Tasks that do not need machines are assigned based only on worker availability.
4. **Update Intervals:** After assigning a task, the worker's and machine's available time slots are updated.
5. **Unscheduled Tasks:** Any tasks that cannot be scheduled are reported at the end.

### Output

- `schedule_worker`: Dictionary of tasks assigned to workers.
- `schedule_machine`: Dictionary of tasks assigned to machines.
- `to_schedule`: List of tasks that couldn't be scheduled.

The algorithm optimally assigns tasks by finding the earliest available slots for both workers and machines, ensuring that deadlines and resource constraints are respected.

## Repository Structure

- **`xelify.py`**  
  Contains the core scheduling algorithms that solve the task-to-worker assignment problem, taking into account the constraints described above.

- **`example.ipynb`**  
  A Jupyter Notebook that demonstrates how to use the `xelify` algorithms with the provided data to solve a practical scheduling problem. This notebook walks you through the process of loading the data, applying the scheduling algorithm, and visualizing the results.

- **Data Files:**
  - `df_hum.csv`: The worker dataset, including worker IDs, skills, availability, and capacity.
  - `df_toy.csv`: The task dataset, including task IDs, duration, required skills, deadlines, and priorities.

