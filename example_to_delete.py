from ortools.sat.python import cp_model

"""
Grape Harvest & Delivery Scheduling — OR-Tools CP-SAT

Locations
---------
  l1  Row 1 start (human begins harvest here)
  l2  Row 1 end   (box 1 collected here)
  l3  Row 2 start
  l4  Row 2 end   (box 2 collected here)
  l5  Collection point  — tractor base
  l6  Handover point    — drone base
  l7  Final destination

Agents
------
  human1   — harvests rows, delivers boxes to l5 or l6
  drone1   — relays box(es) from l6 → l5 (only when needed)
  tractor1 — final leg l5 → l7 once both boxes arrive

Routing decisions (chosen by solver)
--------------------------------------
  For each box the solver picks:
    • Direct path: human delivers box at l5
    • Relay path:  human delivers box at l6, drone carries it to l5

Objective: minimise time for both boxes to reach l7
"""

# ── Scenario definition ──────────────────────────────────────────────────────

agents = ['human1', 'drone1', 'tractor1']
tasks  = [1, 2, 3, 4, 5, 6]

task_names = {
    1: 'Harvest_Row1',   # human1: l1 → l2
    2: 'Deliver_Box1',   # human1: l2 → l5 (direct) or l6 (relay)
    3: 'Harvest_Row2',   # human1: l3 → l4
    4: 'Deliver_Box2',   # human1: l4 → l5 (direct) or l6 (relay)
    5: 'Drone_Relay',    # drone1: l6 → l5  (only if any box routed via l6)
    6: 'Tractor_Final',  # tractor1: l5 → l7
}

# Which agents are allowed per task
task_agents = {
    1: ['human1'],
    2: ['human1'],
    3: ['human1'],
    4: ['human1'],
    5: ['drone1'],
    6: ['tractor1'],
}

# Duration in minutes per task per agent.
# Delivery tasks (2, 4) have two options: direct to l5 vs relay via l6.
task_durations = {
    1: {'human1':  10},
    2: {'human1':  {'direct': 5, 'relay': 8}},
    3: {'human1':  10},
    4: {'human1':  {'direct': 5, 'relay': 8}},
    5: {'drone1':   3},
    6: {'tractor1': 15},
}

# Explicit DAG dependencies
# Tasks 5 and 6 have path-conditional deps; those are enforced separately in the model.
dependencies = {
    1: [],        # Harvest_Row1: root
    2: [1],       # Deliver_Box1: after Harvest_Row1
    3: [2],       # Harvest_Row2: after Deliver_Box1 (+ reposition travel)
    4: [3],       # Deliver_Box2: after Harvest_Row2
    5: [2, 4],    # Drone_Relay:  after deliveries to l6 (path-conditional)
    6: [4, 5],    # Tractor_Final: OR dep on box arrivals at l5 (path-conditional)
}

# Human repositioning travel between rows (after delivering box 1)
reposition_duration = {
    'from_l5': 7,   # l5 → l3
    'from_l6': 9,   # l6 → l3
}


# ── Model ────────────────────────────────────────────────────────────────────

def main():
    model = cp_model.CpModel()
    horizon = 300
    D = task_durations
    R = reposition_duration

    def new_task(name, dur):
        s = model.NewIntVar(0, horizon, f'{name}_s')
        e = model.NewIntVar(0, horizon, f'{name}_e')
        model.Add(e == s + dur)  # end = start + duration
        return s, e

    # Path decisions: True → box goes via l6 (drone relay)
    box1_via_l6 = model.NewBoolVar('box1_via_l6')
    box2_via_l6 = model.NewBoolVar('box2_via_l6')

    # ── Canonical task start/end variables ───────────────────────────────────
    # These are indexed by task ID and used by the dependency loop below.
    # Delivery tasks (2, 4) have two internal variants (direct/relay); the
    # canonical vars track whichever variant the solver activates.
    task_starts = {}
    task_ends   = {}

    # Task 1
    task_starts[1], task_ends[1] = new_task(task_names[1], D[1]['human1'])

    # Task 2 — two path variants; canonical vars bind to active one
    task_starts[2] = model.NewIntVar(0, horizon, 'task2_s')
    task_ends[2]   = model.NewIntVar(0, horizon, 'task2_e')
    t2d_s, t2d_e = new_task('Deliver_Box1_direct', D[2]['human1']['direct'])
    t2r_s, t2r_e = new_task('Deliver_Box1_relay',  D[2]['human1']['relay'])
    model.Add(task_starts[2] == t2d_s).OnlyEnforceIf(box1_via_l6.Not())
    model.Add(task_starts[2] == t2r_s).OnlyEnforceIf(box1_via_l6)
    model.Add(task_ends[2]   == t2d_e).OnlyEnforceIf(box1_via_l6.Not())
    model.Add(task_ends[2]   == t2r_e).OnlyEnforceIf(box1_via_l6)

    # Task 3
    task_starts[3], task_ends[3] = new_task(task_names[3], D[3]['human1'])

    # Task 4 — two path variants
    task_starts[4] = model.NewIntVar(0, horizon, 'task4_s')
    task_ends[4]   = model.NewIntVar(0, horizon, 'task4_e')
    t4d_s, t4d_e = new_task('Deliver_Box2_direct', D[4]['human1']['direct'])
    t4r_s, t4r_e = new_task('Deliver_Box2_relay',  D[4]['human1']['relay'])
    model.Add(task_starts[4] == t4d_s).OnlyEnforceIf(box2_via_l6.Not())
    model.Add(task_starts[4] == t4r_s).OnlyEnforceIf(box2_via_l6)
    model.Add(task_ends[4]   == t4d_e).OnlyEnforceIf(box2_via_l6.Not())
    model.Add(task_ends[4]   == t4r_e).OnlyEnforceIf(box2_via_l6)

    # Tasks 5 & 6
    task_starts[5], task_ends[5] = new_task(task_names[5], D[5]['drone1'])
    task_starts[6], task_ends[6] = new_task(task_names[6], D[6]['tractor1'])

    # ── Apply DAG dependencies (tasks 1–4 simple chain) ─────────────────────
    # Tasks 5 and 6 have path-conditional constraints handled below.
    simple_deps = {t: p for t, p in dependencies.items() if t not in (5, 6)}
    for task, prereqs in simple_deps.items():
        for prereq in prereqs:
            model.Add(task_starts[task] >= task_ends[prereq])

    # Task 3 also needs reposition travel on top of the task-2 dependency
    model.Add(task_starts[3] >= task_ends[2] + R['from_l5']).OnlyEnforceIf(box1_via_l6.Not())
    model.Add(task_starts[3] >= task_ends[2] + R['from_l6']).OnlyEnforceIf(box1_via_l6)

    # ── Task 5: Drone relay (path-conditional) ───────────────────────────────
    # Drone waits at l6 until all boxes routed via l6 have arrived
    model.Add(task_starts[5] >= t2r_e).OnlyEnforceIf(box1_via_l6)
    model.Add(task_starts[5] >= t4r_e).OnlyEnforceIf(box2_via_l6)

    # ── Box arrival times at l5 ──────────────────────────────────────────────
    box1_at_l5 = model.NewIntVar(0, horizon, 'box1_at_l5')
    box2_at_l5 = model.NewIntVar(0, horizon, 'box2_at_l5')

    model.Add(box1_at_l5 == t2d_e).OnlyEnforceIf(box1_via_l6.Not())
    model.Add(box1_at_l5 == task_ends[5]).OnlyEnforceIf(box1_via_l6)

    model.Add(box2_at_l5 == t4d_e).OnlyEnforceIf(box2_via_l6.Not())
    model.Add(box2_at_l5 == task_ends[5]).OnlyEnforceIf(box2_via_l6)

    # ── Task 6: Tractor departs once both boxes are at l5 ───────────────────
    model.Add(task_starts[6] >= box1_at_l5)
    model.Add(task_starts[6] >= box2_at_l5)

    # ── Objective ────────────────────────────────────────────────────────────
    model.Minimize(task_ends[6])

    # ── Solve ─────────────────────────────────────────────────────────────────
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("No solution found.")
        return

    v = solver.Value
    use_l6_b1 = bool(v(box1_via_l6))
    use_l6_b2 = bool(v(box2_via_l6))

    print(f"Optimal: both boxes at l7 by t={int(solver.ObjectiveValue())} min\n")
    print(f"  Agents : {agents}")
    print(f"  Tasks  : {[task_names[t] for t in tasks]}\n")
    print(f"  Box 1 route: {'l2 → l6 → drone → l5' if use_l6_b1 else 'l2 → l5 (direct)'}")
    print(f"  Box 2 route: {'l4 → l6 → drone → l5' if use_l6_b2 else 'l4 → l5 (direct)'}\n")

    print(f"=== {agents[0]} ===")
    print(f"  [{v(task_starts[1]):02d}→{v(task_ends[1]):02d}] Task 1: {task_names[1]}")
    if use_l6_b1:
        print(f"  [{v(t2r_s):02d}→{v(t2r_e):02d}] Task 2: {task_names[2]}  → l6")
        ir_s, ir_e = v(t2r_e), v(t2r_e) + R['from_l6']
    else:
        print(f"  [{v(t2d_s):02d}→{v(t2d_e):02d}] Task 2: {task_names[2]}  → l5")
        ir_s, ir_e = v(t2d_e), v(t2d_e) + R['from_l5']
    print(f"  [{ir_s:02d}→{ir_e:02d}]         Reposition to Row 2 start (l3)")
    print(f"  [{v(task_starts[3]):02d}→{v(task_ends[3]):02d}] Task 3: {task_names[3]}")
    if use_l6_b2:
        print(f"  [{v(t4r_s):02d}→{v(t4r_e):02d}] Task 4: {task_names[4]}  → l6")
    else:
        print(f"  [{v(t4d_s):02d}→{v(t4d_e):02d}] Task 4: {task_names[4]}  → l5")

    if use_l6_b1 or use_l6_b2:
        print(f"\n=== {agents[1]} ===")
        print(f"  [{v(task_starts[5]):02d}→{v(task_ends[5]):02d}] Task 5: {task_names[5]}")

    print(f"\n=== {agents[2]} ===")
    print(f"  [{v(task_starts[6]):02d}→{v(task_ends[6]):02d}] Task 6: {task_names[6]}")


if __name__ == '__main__':
    main()
