from ortools.sat.python import cp_model

# ─────────────────────────────────────────────────────────────────────
# Auto-generated CP-SAT solver
# Targets       : ['Tractor_Final']
# Max duration  : 100 min
# Virtual nodes : ['Deliver_Box1', 'Deliver_Box2']  (abstract; resolved by alternatives)
# Derived-opt.  : ['Drone_Relay']  (run only when triggered)
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
    # Harvest_Row1  (human1, 10 min)
    ts['Harvest_Row1'], te['Harvest_Row1'] = make_iv('Harvest_Row1', 10)
    pr['Harvest_Row1']  = 1
    asg[('Harvest_Row1', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Harvest_Row1'], 10, te['Harvest_Row1'], 'Harvest_Row1_iv'))

    # Harvest_Row2  (human1, 10 min)
    ts['Harvest_Row2'], te['Harvest_Row2'] = make_iv('Harvest_Row2', 10)
    pr['Harvest_Row2']  = 1
    asg[('Harvest_Row2', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Harvest_Row2'], 10, te['Harvest_Row2'], 'Harvest_Row2_iv'))

    # Tractor_Final  (tractor1, 15 min)
    ts['Tractor_Final'], te['Tractor_Final'] = make_iv('Tractor_Final', 15)
    pr['Tractor_Final']  = 1
    asg[('Tractor_Final', 'tractor1')] = 1
    agent_ivs['tractor1'].append(
        model.NewIntervalVar(ts['Tractor_Final'], 15, te['Tractor_Final'], 'Tractor_Final_iv'))

    # ── Optional subtasks (concrete alternatives of virtual nodes) ──────
    # Deliver_Box1_CP  (human1, 5 min) — optional alternative
    _p_Deliver_Box1_CP = model.NewBoolVar('Deliver_Box1_CP')
    pr['Deliver_Box1_CP']  = _p_Deliver_Box1_CP
    asg[('Deliver_Box1_CP', 'human1')] = _p_Deliver_Box1_CP
    ts['Deliver_Box1_CP'], te['Deliver_Box1_CP'] = make_iv('Deliver_Box1_CP', 5)
    agent_ivs['human1'].append(
        model.NewOptionalIntervalVar(ts['Deliver_Box1_CP'], 5, te['Deliver_Box1_CP'], _p_Deliver_Box1_CP, 'Deliver_Box1_CP_iv'))

    # Deliver_Box1_HP  (human1, 5 min) — optional alternative
    _p_Deliver_Box1_HP = model.NewBoolVar('Deliver_Box1_HP')
    pr['Deliver_Box1_HP']  = _p_Deliver_Box1_HP
    asg[('Deliver_Box1_HP', 'human1')] = _p_Deliver_Box1_HP
    ts['Deliver_Box1_HP'], te['Deliver_Box1_HP'] = make_iv('Deliver_Box1_HP', 5)
    agent_ivs['human1'].append(
        model.NewOptionalIntervalVar(ts['Deliver_Box1_HP'], 5, te['Deliver_Box1_HP'], _p_Deliver_Box1_HP, 'Deliver_Box1_HP_iv'))

    # Deliver_Box2_CP  (human1, 5 min) — optional alternative
    _p_Deliver_Box2_CP = model.NewBoolVar('Deliver_Box2_CP')
    pr['Deliver_Box2_CP']  = _p_Deliver_Box2_CP
    asg[('Deliver_Box2_CP', 'human1')] = _p_Deliver_Box2_CP
    ts['Deliver_Box2_CP'], te['Deliver_Box2_CP'] = make_iv('Deliver_Box2_CP', 5)
    agent_ivs['human1'].append(
        model.NewOptionalIntervalVar(ts['Deliver_Box2_CP'], 5, te['Deliver_Box2_CP'], _p_Deliver_Box2_CP, 'Deliver_Box2_CP_iv'))

    # Deliver_Box2_HP  (human1, 5 min) — optional alternative
    _p_Deliver_Box2_HP = model.NewBoolVar('Deliver_Box2_HP')
    pr['Deliver_Box2_HP']  = _p_Deliver_Box2_HP
    asg[('Deliver_Box2_HP', 'human1')] = _p_Deliver_Box2_HP
    ts['Deliver_Box2_HP'], te['Deliver_Box2_HP'] = make_iv('Deliver_Box2_HP', 5)
    agent_ivs['human1'].append(
        model.NewOptionalIntervalVar(ts['Deliver_Box2_HP'], 5, te['Deliver_Box2_HP'], _p_Deliver_Box2_HP, 'Deliver_Box2_HP_iv'))

    # ── Virtual nodes (canonical vars bound to whichever alternative runs) ─
    # Deliver_Box1  → exactly one of ['Deliver_Box1_CP', 'Deliver_Box1_HP']
    ts['Deliver_Box1'] = model.NewIntVar(0, horizon, 'Deliver_Box1_s')
    te['Deliver_Box1'] = model.NewIntVar(0, horizon, 'Deliver_Box1_e')
    pr['Deliver_Box1']  = model.NewBoolVar('Deliver_Box1_active')
    model.AddExactlyOne([_p_Deliver_Box1_CP, _p_Deliver_Box1_HP])
    model.Add(pr['Deliver_Box1'] == 1)
    model.Add(ts['Deliver_Box1'] == ts['Deliver_Box1_CP']).OnlyEnforceIf(_p_Deliver_Box1_CP)
    model.Add(te['Deliver_Box1'] == te['Deliver_Box1_CP']).OnlyEnforceIf(_p_Deliver_Box1_CP)
    model.Add(ts['Deliver_Box1'] == ts['Deliver_Box1_HP']).OnlyEnforceIf(_p_Deliver_Box1_HP)
    model.Add(te['Deliver_Box1'] == te['Deliver_Box1_HP']).OnlyEnforceIf(_p_Deliver_Box1_HP)

    # Deliver_Box2  → exactly one of ['Deliver_Box2_CP', 'Deliver_Box2_HP']
    ts['Deliver_Box2'] = model.NewIntVar(0, horizon, 'Deliver_Box2_s')
    te['Deliver_Box2'] = model.NewIntVar(0, horizon, 'Deliver_Box2_e')
    pr['Deliver_Box2']  = model.NewBoolVar('Deliver_Box2_active')
    model.AddExactlyOne([_p_Deliver_Box2_CP, _p_Deliver_Box2_HP])
    model.Add(pr['Deliver_Box2'] == 1)
    model.Add(ts['Deliver_Box2'] == ts['Deliver_Box2_CP']).OnlyEnforceIf(_p_Deliver_Box2_CP)
    model.Add(te['Deliver_Box2'] == te['Deliver_Box2_CP']).OnlyEnforceIf(_p_Deliver_Box2_CP)
    model.Add(ts['Deliver_Box2'] == ts['Deliver_Box2_HP']).OnlyEnforceIf(_p_Deliver_Box2_HP)
    model.Add(te['Deliver_Box2'] == te['Deliver_Box2_HP']).OnlyEnforceIf(_p_Deliver_Box2_HP)

    # ── Derived-optional tasks (presence driven by OR-deps) ────────────
    # Drone_Relay  (drone1, 3 min) — active iff any of ['Deliver_Box1_HP', 'Deliver_Box2_HP'] is active
    _p_Drone_Relay = model.NewBoolVar('Drone_Relay')
    pr['Drone_Relay']  = _p_Drone_Relay
    asg[('Drone_Relay', 'drone1')] = _p_Drone_Relay
    ts['Drone_Relay'], te['Drone_Relay'] = make_iv('Drone_Relay', 3)
    agent_ivs['drone1'].append(
        model.NewOptionalIntervalVar(ts['Drone_Relay'], 3, te['Drone_Relay'], _p_Drone_Relay, 'Drone_Relay_iv'))
    model.AddImplication(_p_Deliver_Box1_HP, _p_Drone_Relay)  # if _p_Deliver_Box1_HP is active, Drone_Relay must run
    model.AddImplication(_p_Deliver_Box2_HP, _p_Drone_Relay)  # if _p_Deliver_Box2_HP is active, Drone_Relay must run
    model.AddBoolOr([_p_Drone_Relay.Not(), _p_Deliver_Box1_HP, _p_Deliver_Box2_HP])
    # ^ Drone_Relay only runs if at least one of ['Deliver_Box1_HP', 'Deliver_Box2_HP'] is active

    # ── Dependencies ──────────────────────────────────────────────────
    # Deliver_Box1 starts after Harvest_Row1  (AND)
    model.Add(ts['Deliver_Box1'] >= te['Harvest_Row1'])
    # Harvest_Row2 starts after Deliver_Box1  (AND)
    model.Add(ts['Harvest_Row2'] >= te['Deliver_Box1'])
    # Deliver_Box2 starts after Harvest_Row2  (AND)
    model.Add(ts['Deliver_Box2'] >= te['Harvest_Row2'])
    # Drone_Relay starts after Deliver_Box1_HP  (AND_IF_ACTIVE)
    model.Add(ts['Drone_Relay'] >= te['Deliver_Box1_HP']).OnlyEnforceIf([_p_Drone_Relay, _p_Deliver_Box1_HP])
    # Drone_Relay starts after Deliver_Box2_HP  (AND_IF_ACTIVE)
    model.Add(ts['Drone_Relay'] >= te['Deliver_Box2_HP']).OnlyEnforceIf([_p_Drone_Relay, _p_Deliver_Box2_HP])
    # Tractor_Final starts after Deliver_Box1_CP  (AND_IF_ACTIVE)
    model.Add(ts['Tractor_Final'] >= te['Deliver_Box1_CP']).OnlyEnforceIf(_p_Deliver_Box1_CP)
    # Tractor_Final starts after Deliver_Box2_CP  (AND_IF_ACTIVE)
    model.Add(ts['Tractor_Final'] >= te['Deliver_Box2_CP']).OnlyEnforceIf(_p_Deliver_Box2_CP)
    # Tractor_Final starts after Drone_Relay  (AND_IF_ACTIVE)
    model.Add(ts['Tractor_Final'] >= te['Drone_Relay']).OnlyEnforceIf(_p_Drone_Relay)
    # Deliver_Box1_CP starts after Harvest_Row1  (AND)
    model.Add(ts['Deliver_Box1_CP'] >= te['Harvest_Row1']).OnlyEnforceIf(_p_Deliver_Box1_CP)
    # Deliver_Box1_HP starts after Harvest_Row1  (AND)
    model.Add(ts['Deliver_Box1_HP'] >= te['Harvest_Row1']).OnlyEnforceIf(_p_Deliver_Box1_HP)
    # Deliver_Box2_CP starts after Harvest_Row2  (AND)
    model.Add(ts['Deliver_Box2_CP'] >= te['Harvest_Row2']).OnlyEnforceIf(_p_Deliver_Box2_CP)
    # Deliver_Box2_HP starts after Harvest_Row2  (AND)
    model.Add(ts['Deliver_Box2_HP'] >= te['Harvest_Row2']).OnlyEnforceIf(_p_Deliver_Box2_HP)

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

    virtual_nodes = ['Deliver_Box1', 'Deliver_Box2']
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