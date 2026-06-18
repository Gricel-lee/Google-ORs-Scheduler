from ortools.sat.python import cp_model

# ─────────────────────────────────────────────────────────────────────
# Auto-generated CP-SAT solver
# Targets       : ['Tractor_Final']
# Max duration  : 100 min
# Virtual nodes : []  (abstract; resolved by alternatives)
# Derived-opt.  : []  (run only when triggered)
# ─────────────────────────────────────────────────────────────────────


def main():
    model = cp_model.CpModel()
    horizon = 100

    def make_iv(name, dur):
        s = model.NewIntVar(0, horizon, name + "_s")
        e = model.NewIntVar(0, horizon, name + "_e")
        model.Add(e == s + dur)
        return s, e

    ts  = {}   # ts[task_id]              -> start IntVar
    te  = {}   # te[task_id]              -> end   IntVar
    pr  = {}   # pr[task_id]              -> BoolVar | 1 (presence/active)
    asg = {}   # asg[(task_id, agent_id)] -> BoolVar | 1
    agent_ivs = {a: [] for a in ['human1', 'drone1', 'tractor1']}

    # ── Mandatory concrete tasks ───────────────────────────────────────
    # Deliver_Box1_CP  (human1, 5 min)
    ts['Deliver_Box1_CP'], te['Deliver_Box1_CP'] = make_iv('Deliver_Box1_CP', 5)
    pr['Deliver_Box1_CP']  = 1
    asg[('Deliver_Box1_CP', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Deliver_Box1_CP'], 5, te['Deliver_Box1_CP'], 'Deliver_Box1_CP_iv'))

    # Deliver_Box1_HP  (human1, 5 min)
    ts['Deliver_Box1_HP'], te['Deliver_Box1_HP'] = make_iv('Deliver_Box1_HP', 5)
    pr['Deliver_Box1_HP']  = 1
    asg[('Deliver_Box1_HP', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Deliver_Box1_HP'], 5, te['Deliver_Box1_HP'], 'Deliver_Box1_HP_iv'))

    # Deliver_Box2_CP  (human1, 5 min)
    ts['Deliver_Box2_CP'], te['Deliver_Box2_CP'] = make_iv('Deliver_Box2_CP', 5)
    pr['Deliver_Box2_CP']  = 1
    asg[('Deliver_Box2_CP', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Deliver_Box2_CP'], 5, te['Deliver_Box2_CP'], 'Deliver_Box2_CP_iv'))

    # Deliver_Box2_HP  (human1, 5 min)
    ts['Deliver_Box2_HP'], te['Deliver_Box2_HP'] = make_iv('Deliver_Box2_HP', 5)
    pr['Deliver_Box2_HP']  = 1
    asg[('Deliver_Box2_HP', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Deliver_Box2_HP'], 5, te['Deliver_Box2_HP'], 'Deliver_Box2_HP_iv'))

    # Drone_Relay  (drone1, 3 min)
    ts['Drone_Relay'], te['Drone_Relay'] = make_iv('Drone_Relay', 3)
    pr['Drone_Relay']  = 1
    asg[('Drone_Relay', 'drone1')] = 1
    agent_ivs['drone1'].append(
        model.NewIntervalVar(ts['Drone_Relay'], 3, te['Drone_Relay'], 'Drone_Relay_iv'))

    # Tractor_Final  (tractor1, 15 min)
    ts['Tractor_Final'], te['Tractor_Final'] = make_iv('Tractor_Final', 15)
    pr['Tractor_Final']  = 1
    asg[('Tractor_Final', 'tractor1')] = 1
    agent_ivs['tractor1'].append(
        model.NewIntervalVar(ts['Tractor_Final'], 15, te['Tractor_Final'], 'Tractor_Final_iv'))

    # ── Optional subtasks (concrete alternatives of virtual nodes) ──────
    # ── Dependencies ──────────────────────────────────────────────────
    _dep_Drone_Relay_Deliver_Box1_HP = model.NewBoolVar('Drone_Relay_after_Deliver_Box1_HP')
    model.Add(ts['Drone_Relay'] >= te['Deliver_Box1_HP']).OnlyEnforceIf(_dep_Drone_Relay_Deliver_Box1_HP)
    _dep_Drone_Relay_Deliver_Box2_HP = model.NewBoolVar('Drone_Relay_after_Deliver_Box2_HP')
    model.Add(ts['Drone_Relay'] >= te['Deliver_Box2_HP']).OnlyEnforceIf(_dep_Drone_Relay_Deliver_Box2_HP)
    model.AddBoolOr([_dep_Drone_Relay_Deliver_Box1_HP, _dep_Drone_Relay_Deliver_Box2_HP])
    # ^ Drone_Relay starts after ANY of ['Deliver_Box1_HP', 'Deliver_Box2_HP']
    _dep_Tractor_Final_Deliver_Box1_CP = model.NewBoolVar('Tractor_Final_after_Deliver_Box1_CP')
    model.Add(ts['Tractor_Final'] >= te['Deliver_Box1_CP']).OnlyEnforceIf(_dep_Tractor_Final_Deliver_Box1_CP)
    _dep_Tractor_Final_Deliver_Box2_CP = model.NewBoolVar('Tractor_Final_after_Deliver_Box2_CP')
    model.Add(ts['Tractor_Final'] >= te['Deliver_Box2_CP']).OnlyEnforceIf(_dep_Tractor_Final_Deliver_Box2_CP)
    _dep_Tractor_Final_Drone_Relay = model.NewBoolVar('Tractor_Final_after_Drone_Relay')
    model.Add(ts['Tractor_Final'] >= te['Drone_Relay']).OnlyEnforceIf(_dep_Tractor_Final_Drone_Relay)
    model.AddBoolOr([_dep_Tractor_Final_Deliver_Box1_CP, _dep_Tractor_Final_Deliver_Box2_CP, _dep_Tractor_Final_Drone_Relay])
    # ^ Tractor_Final starts after ANY of ['Deliver_Box1_CP', 'Deliver_Box2_CP', 'Drone_Relay']

    # ── Agent no-overlap ──────────────────────────────────────────────
    for agent_id, ivs in agent_ivs.items():
        if len(ivs) > 1:
            model.AddNoOverlap(ivs)

    # ── Objective: minimise completion of target tasks ────────────────
    model.Minimize(te['Tractor_Final'])

    # ── Solve ─────────────────────────────────────────────────────────
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("No solution found within constraints.")
        return

    v = solver.Value
    print(f"Solution — makespan: {int(solver.ObjectiveValue())} min\n")

    virtual_nodes = []
    for agent_id in agent_ivs:
        schedule = []
        for (tid, aid), presence in asg.items():
            if aid != agent_id or tid in virtual_nodes:
                continue
            active = presence if isinstance(presence, int) else v(presence)
            if active:
                schedule.append((v(ts[tid]), v(te[tid]), tid))
        if not schedule:
            continue
        schedule.sort()
        print(f"=== {agent_id} ===")
        for s, e, tid in schedule:
            print(f"  [{s:02d}→{e:02d}] {tid}")
        print()


if __name__ == '__main__':
    main()