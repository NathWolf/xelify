#SCRIT WITH FUCTIONS AND ALGORITHMS
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import MaxNLocator
#import pulp as pl

import gurobipy as gp
from gurobipy import GRB, quicksum

                       #for saving best objects
class functions:
    def Norm_worktimes(worker_schedules,initial_time=9):
    #Real working hours are between 9h and 18h. This fuction change it so we can start from 0
        worker_schedules_norm = {}
        for i in worker_schedules:
            worker_schedules_norm[i] = (max(worker_schedules[i][0]-initial_time,0)*60, (worker_schedules[i][1]-initial_time)*60)
        return worker_schedules_norm

    def Available_intervals(available_set, busy_interval):
        #modify the set of available intervals (available_set) to exclude the new busy interval
        #busy_interval is inside an interval in the available_interval set. The function finds and split the interval into two 

        added_cut = 0
        new_intervals_set = []
        
        for interval in available_set:
            if added_cut != 1: #only break one interval    
                if interval[0] <= busy_interval[0] and interval[1] >= busy_interval[1]:
                    if interval[0] != busy_interval[0]:
                        new_intervals_set.append([interval[0], busy_interval[0]])
                        added_cut = 1
                    if interval[1] != busy_interval[1]:
                        new_intervals_set.append([busy_interval[1], interval[1]])
                        added_cut = 1
                else:
                    new_intervals_set.append(interval)
            else:
                new_intervals_set.append(interval)

        return new_intervals_set
    
    def Available_intervals_sm(available_set, busy_interval, which_interval):
        
        print('old interval set: ',available_set)
        print('busy interval: ',busy_interval)
        print('which interval: ',which_interval)
        print('interval to cut: ',available_set[which_interval])

        new_intervals_set = {k:v for k,v in available_set.items() if k != which_interval}
        print('new interval set w/o cut: ',new_intervals_set)

        #for interval in available_set:
        interval = available_set[which_interval]
        print('interval: ',interval)
        
        new_intervals_set[which_interval] = [interval[0], busy_interval[0]]
        new_intervals_set[len(new_intervals_set)+1] = [busy_interval[1], interval[1]]    
        print('new interval set: ',new_intervals_set)

        return new_intervals_set
    
class algorithms:
    def Jackson_bw(num_tareas, num_maquinas, num_trabajadores, tiempos_procesamiento, habilidades_trabajadores, horarios_trabajadores, deadlines, machine_required):
        #! Ordenar tareas por deadline
        orden_tareas = np.argsort(deadlines) #* assumtion
        to_schedule = orden_tareas.copy()
        
        schedule_worker = {i:[] for i in range(1,num_trabajadores+1)}
        schedule_machine = {i:[] for i in range(num_maquinas)}

        #generate available intervals for machines and workers
        available_intervals_machine = {i:[[0,max(deadlines)]] for i in range(num_maquinas)}
        available_intervals_worker = {i:[[horarios_trabajadores[i][0],horarios_trabajadores[i][1]]] for i in range(1,num_trabajadores+1)}

        n_iter = 0
        #Scheduling according to Johnson algorithm
        while n_iter < 1: # or len(to_schedule) != 0:
            for task in [i for i in to_schedule if len(machine_required[i]) != 0]:
                best_time = float('inf')
                best_machine = []
                best_worker = -1
                for worker in range(1,num_trabajadores+1): 
                #! Verify if worker can use all machines needed in the task
                    if 0 not in [habilidades_trabajadores[worker][machine] for machine in machine_required[task]]:   
                        #! Verify if worker is available to finish the task before the deadline
                        for work_interval in available_intervals_worker[worker]:
                            interval = [work_interval[0], work_interval[0] + tiempos_procesamiento[task]]
                            if interval[1] <= deadlines[task] and interval[1] <= work_interval[1]:
                                this_interval = {m: 0 for m in machine_required[task]}
                                #! Verify if all machines needed are available in the time slot
                                for machine in machine_required[task]:
                                    for machine_interval in available_intervals_machine[machine]:
                                        if interval[0] >= machine_interval[0] and interval[1] <= machine_interval[1]:
                                            this_interval[machine] = 1
                                        elif this_interval[machine] != 1: #if there is one slot available, then it is enough
                                            this_interval[machine] = 0 #todo: more efficient break
                                #! After checking that all required machine are available in the time slot, check if it is the best time
                                if 0 not in this_interval.values():
                                    if interval[1] < best_time:
                                        best_interval = interval
                                        best_time = interval[1]
                                        best_machine = machine_required[task]
                                        best_worker = worker - 1
                                        #! Set machine and worker to the task
        
                #! Asign task to the best machine and worker and update the available intervals
                if len(best_machine) != 0 and best_worker != -1:
                    # remove task from tasks to_schedule
                    to_schedule = np.delete(to_schedule, np.where(to_schedule == task))

                    # change old available intervals
                    schedule_worker[best_worker+1].append([task,best_machine,(best_time - tiempos_procesamiento[task], best_time)])
                    available_intervals_worker[best_worker+1] = functions.Available_intervals(available_intervals_worker[best_worker+1], best_interval)     
                    for machine in best_machine:
                        schedule_machine[machine].append([task,best_worker+1,(best_time - tiempos_procesamiento[task], best_time)]) 
                        available_intervals_machine[machine] = functions.Available_intervals(available_intervals_machine[machine], best_interval) 
                    if n_iter > 1: 
                        print('task %s scheduled in iteration %s' % (task,n_iter))
                        

            #now schedule the tasks that do not need machines 
            for task in [i for i in to_schedule if len(machine_required[i]) == 0]:
                best_time = float('inf')
                best_worker = -1
                for worker in range(1,num_trabajadores+1):
                    for work_interval in available_intervals_worker[worker]:
                        interval = [work_interval[0], work_interval[0] + tiempos_procesamiento[task]]
                        if interval[1] <= deadlines[task] and interval[1] <= work_interval[1]:
                            if interval[1] < best_time:
                                best_interval = interval
                                best_time = interval[1]
                                best_worker = worker - 1
                if best_worker != -1:
                    # remove task from tasks to_schedule
                    to_schedule = np.delete(to_schedule, np.where(to_schedule == task))

                    # change old available intervals
                    schedule_worker[best_worker+1].append([task,[],(best_time - tiempos_procesamiento[task], best_time)])
                    available_intervals_worker[best_worker+1] = functions.Available_intervals(available_intervals_worker[best_worker+1], best_interval)
                else:
                    print('task %s could not be scheduled' %task)
                    print('time of task: ',tiempos_procesamiento[task])
                    
            n_iter += 1

        print('task left to schedule: ', len(to_schedule))
        for task in to_schedule:
            print('task %s could not be scheduled' % task)
            print('machine required: ',machine_required[task])

        return schedule_worker,schedule_machine,to_schedule

    def Jackson_bw_sm(num_tareas, num_maquinas, num_trabajadores, tiempos_procesamiento, habilidades_trabajadores, horarios_trabajadores, deadlines, machine_required,machine_capacity):
        #! Ordenar tareas por deadline
        orden_tareas = np.argsort(deadlines) #* assumtion
        to_schedule = orden_tareas.copy()
        
        schedule_worker = {i:[] for i in range(1,num_trabajadores+1)}
        schedule_machine = {i:[] for i in range(num_maquinas)}

        #available_intervals_machine = {i:{j:[0,max(deadlines)] for j in range(1,machine_capacity[i]+1)} for i in range(num_maquinas)}
        available_intervals_machine = {i:[[0,max(deadlines)] for j in range(1,machine_capacity[i]+1)] for i in range(num_maquinas)}
        #print(available_intervals_machine)
        available_intervals_worker = {i:[[horarios_trabajadores[i][j][0],horarios_trabajadores[i][j][1]] for j in range(len(horarios_trabajadores[i]))] for i in range(1,num_trabajadores+1)}

        #print(available_intervals_worker)

        n_iter = 0
        #Scheduling according to Johnson algorithm
        while n_iter < 1: # or len(to_schedule) != 0:
            for task in [i for i in to_schedule if len(machine_required[i]) != 0]:
                best_time = float('inf')
                best_machine = []
                best_worker = -1
                for worker in range(1,num_trabajadores+1): 
                #! Verify if worker can use all machines needed in the task
                    #if 0 not in [habilidades_trabajadores[worker][machine] for machine in machine_required[task]]:   
                    w = 0
                    for machine_req in machine_required[task]:
                        if machine_req in habilidades_trabajadores[worker]:
                            w += 1
                        else: #if one machine is not available, then go to the next worker
                            break
                    if w == len(machine_required[task]):
                        #! Verify if worker is available to finish the task before the deadline
                        for work_interval in available_intervals_worker[worker]:
                            interval = [work_interval[0], work_interval[0] + tiempos_procesamiento[task]]
                            if interval[1] <= deadlines[task] and interval[1] <= work_interval[1]:
                                if n_iter > 0:
                                    print('worker %s can do task %s in interval %s' %(worker,task,interval))
                                this_interval = {m: 0 for m in machine_required[task]}
                                #! Verify if all machines needed are available in the time slot
                                if n_iter > 0:
                                    print('machine required: ',machine_required[task])
                                for machine in machine_required[task]:
                                    for machine_interval in available_intervals_machine[machine]: 
                                        if interval[0] >= machine_interval[0] and interval[1] <= machine_interval[1]:
                                            if n_iter > 0:
                                                print('machine %s is available in interval %s' %(machine,machine_interval))
                                            this_interval[machine] = 1 
                                        #elif this_interval[machine] < 1: #if there is one slot available, then it is enough
                                        #    this_interval[machine] = 0 #todo: more efficient break  
                                #! After checking that all required machine are available in the time slot, check if it is the best time
                                if 0 not in this_interval.values():
                                    if n_iter > 0:
                                        print('all machines available for worker %s to do task %s' %(worker,task))
                                    if interval[1] < best_time:
                                        best_interval = interval
                                        best_time = interval[1]
                                        best_machine = machine_required[task]
                                        best_worker = worker - 1
                                        #! Set machine and worker to the task
                                        
                #! Asign task to the best machine and worker and update the available intervals
                if len(best_machine) != 0 and best_worker != -1:
                    # remove task from tasks to_schedule
                    to_schedule = np.delete(to_schedule, np.where(to_schedule == task))

                    # change old available intervals
                    schedule_worker[best_worker+1].append([task,best_machine,(best_time - tiempos_procesamiento[task], best_time)])
                    available_intervals_worker[best_worker+1] = functions.Available_intervals(available_intervals_worker[best_worker+1], best_interval)     
                    
                    for machine in best_machine:
                        schedule_machine[machine].append([task,best_worker+1,(best_time - tiempos_procesamiento[task], best_time)]) 
                        available_intervals_machine[machine] = functions.Available_intervals(available_intervals_machine[machine], best_interval)
                        #available_intervals_machine[machine] = functions.Available_intervals_sm(available_intervals_machine[machine], best_interval, key_interval[machine])
            
            #now schedule the tasks that do not need machines 
            for task in [i for i in to_schedule if len(machine_required[i]) == 0]:
                #print('task %s does not need a machine' % task)
                best_time = float('inf')
                best_worker = -1
                for worker in range(1,num_trabajadores+1):
                    for work_interval in available_intervals_worker[worker]:
                        interval = [work_interval[0], work_interval[0] + tiempos_procesamiento[task]]
                        if interval[1] <= deadlines[task] and interval[1] <= work_interval[1]:
                            if interval[1] < best_time:
                                best_interval = interval
                                best_time = interval[1]
                                best_worker = worker - 1
                if best_worker != -1:
                    # remove task from tasks to_schedule
                    to_schedule = np.delete(to_schedule, np.where(to_schedule == task))

                    # change old available intervals
                    schedule_worker[best_worker+1].append([task,[],(best_time - tiempos_procesamiento[task], best_time)])
                    available_intervals_worker[best_worker+1] = functions.Available_intervals(available_intervals_worker[best_worker+1], best_interval)
                    #print('yes, could be scheduled')
                else:
                    print('task %s could not be scheduled' %task)
                    #print('machine required: ',machine_required[task])      
                    print('time of task: ',tiempos_procesamiento[task])  
        
            n_iter += 1

        #print(available_intervals_machine)
        #print(available_intervals_worker)

        return schedule_worker,schedule_machine,to_schedule

    def Jackson_bw_cap(num_tareas, num_maquinas, num_trabajadores, tiempos_procesamiento, habilidades_trabajadores, horarios_trabajadores, deadlines, machine_required, machine_capacity):
        '''
            use a Johnson like approach to schedule the tasks to the workers that can do them in the best time
            in this version, there can be more than one equal machine (capacity), so the task is assigned to the first one in the list if available
            also consider that some task dont need a machine
        '''    
        orden_tareas = np.argsort(deadlines) 
        to_schedule = orden_tareas.copy()
        
        schedule_worker = {i:[] for i in range(1,num_trabajadores+1)}
        schedule_machine = {i:{j: [] for j in range(1,machine_capacity[i]+1)} for i in range(num_maquinas)}

        #generate available intervals for machines and workers
        available_intervals_machine = {i:{j:[[0,max(deadlines)]] for j in range(1,machine_capacity[i]+1)} for i in range(num_maquinas)}
        available_intervals_worker = {i:[[horarios_trabajadores[i][0],horarios_trabajadores[i][1]]] for i in range(1,num_trabajadores+1)}

        print('available intervals machine: ',available_intervals_machine)
        print('available intervals worker: ',available_intervals_worker)

        n_iter = 0
        while n_iter <2: 
            for task in to_schedule:
                print('scheduling task ',task)
                best_time = float('inf')
                best_machine = []
                best_worker = -1
                for worker in range(1,num_trabajadores+1): 
                    if sum(machine_required[task]) == 0: #If task does not need a machine
                        #! Verify if worker is available to finish the task before the deadline
                        for work_interval in available_intervals_worker[worker]:
                            interval = [work_interval[0], work_interval[0] + tiempos_procesamiento[task]]
                            if interval[1] <= deadlines[task] and interval[1] <= work_interval[1]:
                                if interval[1] < best_time:
                                    best_interval = interval
                                    best_time = interval[1]
                                    best_machine = []
                                    best_worker = worker - 1

                    else: #If task does need a machine
                    #! Verify if worker can use all machines needed in the task
                        if 0 not in [habilidades_trabajadores[worker][machine] for machine in machine_required[task]]:   
                            #! Verify if worker is available to finish the task before the deadline
                            for work_interval in available_intervals_worker[worker]:
                                interval = [work_interval[0], work_interval[0] + tiempos_procesamiento[task]]
                                if interval[1] <= deadlines[task] and interval[1] <= work_interval[1]:
                                    which = {m: 0 for m in machine_required[task]}
                                    #! Verify if all machines needed are available in the time slot
                                    for machine in machine_required[task]:
                                        for j in range(1,machine_capacity[machine]+1):
                                            if which[machine] == 0:
                                                for machine_interval in available_intervals_machine[machine][j]:
                                                    if which[machine] == 0:
                                                        if interval[0] >= machine_interval[0] and interval[1] <= machine_interval[1]:
                                                            which[machine] = j                                              
                                    #! After checking that all required machine are available in the time slot, check if it is the best time
                                    if 0 not in which.values():
                                        if interval[1] < best_time:
                                            best_interval = interval
                                            best_time = interval[1]
                                            best_machine = which
                                            best_worker = worker - 1
                                            #! Set machine and worker to the task
                                            
                #! Asign task to the best machine and worker and update the available intervals
                if best_worker != -1:
                    print('intervalo task %s: ' % task)
                    print(best_interval)

                    # remove task from tasks to_schedule
                    to_schedule = np.delete(to_schedule, np.where(to_schedule == task))

                    # change old available intervals
                    schedule_worker[best_worker+1].append([task,best_machine,(best_time - tiempos_procesamiento[task], best_time)])
                    available_intervals_worker[best_worker+1] = functions.Available_intervals(available_intervals_worker[best_worker+1], best_interval)     
                    
                    print('new available intervals worker %s: ' % (best_worker+1))
                    print(available_intervals_worker[best_worker+1])

                    if len(best_machine) != 0:
                        for machine in machine_required[task]:
                            schedule_machine[machine][best_machine[machine]].append([task,best_worker+1,(best_time - tiempos_procesamiento[task], best_time)]) 
                            available_intervals_machine[machine][which[machine]] = functions.Available_intervals(available_intervals_machine[machine][which[machine]], best_interval) 

                            print('new available intervals machine %s: ' % machine)
                            print(available_intervals_machine[machine][which[machine]]) 

            n_iter += 1

        return schedule_worker,schedule_machine,to_schedule  
        
class models:
    def jp_network_gu(data):
        #! Model for the Job Shop Scheduling Problem using Gurobi
        model = gp.Model('Job Shop Scheduling Problem')
        model.Params.TimeLimit = 600
        model.Params.MIPGap = 0.05

        #! Data
        Workers,Paths,Route,Machines,Periods,Habilidades,deadlines,capacity,t_in,t_out = data

        #create the matrix of nodes 
        Nodes = [(m,t) for m in Machines for t in Periods for n in range(1,len(Machines)*len(Periods)+1)]
        Edges = [[(m1,t),(m2,t+1)] for m1 in Machines for m2 in Machines for t in Periods]

        #! Variables
        x = {}
        for w in Workers:
            for p in Paths:
                for e in Edges: #edges NxN [i for i in Nodes if i[0] in p and i[1] in [t_in[w],t_out[w]]]:
                    x[w,p,e] = model.addVar(vtype=GRB.BINARY, name='x(%s,%s,%s)' % (w,p,e))  

        #! Objective
        #minimize the number of x after the deadline
        model.setObjective(quicksum(x[w,p,e] for w in Workers for p in Paths for e in [i for i in Edges if (i[0][0] in p and i[1][0] in p and i[1][1] > deadlines[w])]), GRB.MINIMIZE)

        #! Constraints
        for w in Workers:
            #worker start in period t_in[w] and finish in period t_out[w]
            model.addConstr(quicksum(x[w,p,e] for p in Paths for e in [i for i in Edges if (i[1][0] in p and i[1][0] == t_in[w])]) == 1, name='start(%s)' % w)
            model.addConstr(quicksum(x[w,p,e] for p in Paths for e in [i for i in Edges if (i[1][0] in p and i[1][1] == t_out[w])]) == 1, name='finish(%s)' % w)
            for n in [(m,t) for (m,t) in Nodes if t < t_out[w] and t > t_in[w] and m in Habilidades[w]]:
                #sum of edges that enter node <= sum of edges that leave node, then (1,0) is allowed
                model.addConstr(quicksum(x[w,p,e] for p in Paths for e in [(n1,n2) for (n1,n2) in Edges if n2==n]) == quicksum(x[w,p,e] for p in Paths for e in [(n1,n2) for (n1,n2) in Edges if n1==n]), name='continuity(%s,%s)' % (w,n))
            #a worker can only follow one path at a time
            model.addConstr(quicksum(x[w,p,e] for p in Paths for e in Edges if e[1][0] in p) <= 1, name='one_path(%s)' % w)
        #there is a maximum capacity in the nodes
        for (m,t) in Nodes:
            model.addConstr(quicksum(x[w,p,e] for w in Workers for p in Paths for e in Edges if e[1] == (m,t)) <= capacity[m], name='capacity(%s,%s)' % (m,t))
        #only one worker follows a path 
        for p in Paths:
            model.addConstr(quicksum(x[w,p,e] for w in Workers for e in Edges if e[1][0] in p) <= 1, name='one_worker(%s)' % p)
        #the path has to be followed in order
        for p in Paths: #p = [m1,m2,m3,...] a path is a list of machines that the worker has to follow, starting from the head of first edge in which x[w,p,e] = 1     
            for j in range(len(Route[p])-1): #m in p[:-1]:
                for n in [i for i in Nodes if i[0]==Route[p][j]]: #n = (m,t) is a node in the route
                    model.addConstr(quicksum(x[w,p,(n1,n)] for w in Workers for (n1,n) in Edges) <= quicksum(x[w,p,(n,n2)] for w in Workers for (n,n2) in Edges if n2[0]==Route[p][j+1] and n2[1]==n[1]+1))
                    
        model.update()

        #! Solve
        model.optimize()

        #! Results
        if model.status == GRB.OPTIMAL:
            print('Optimal objective: %g' % model.objVal)
            #save variables
            x_sol = {}
            for w in Workers:
                for p in Paths:
                    for e in Edges:
                        x_sol[w,p,e] = x[w,p,e].x
            return x_sol
        else:
            print('No solution')

        return 
