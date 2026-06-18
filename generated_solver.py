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
    # Harvest_Row1  (human1, 3 min)
    ts['Harvest_Row1'], te['Harvest_Row1'] = make_iv('Harvest_Row1', 3)
    pr['Harvest_Row1']  = 1
    asg[('Harvest_Row1', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Harvest_Row1'], 3, te['Harvest_Row1'], 'Harvest_Row1_iv'))

    # Harvest_Row2  (human1, 20 min)
    ts['Harvest_Row2'], te['Harvest_Row2'] = make_iv('Harvest_Row2', 20)
    pr['Harvest_Row2']  = 1
    asg[('Harvest_Row2', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Harvest_Row2'], 20, te['Harvest_Row2'], 'Harvest_Row2_iv'))

    # Tractor_Final  (tractor1, 30 min)
    ts['Tractor_Final'], te['Tractor_Final'] = make_iv('Tractor_Final', 30)
    pr['Tractor_Final']  = 1
    asg[('Tractor_Final', 'tractor1')] = 1
    agent_ivs['tractor1'].append(
        model.NewIntervalVar(ts['Tractor_Final'], 30, te['Tractor_Final'], 'Tractor_Final_iv'))

    # ── Optional subtasks (concrete alternatives of virtual nodes) ──────
    # Deliver_Box1_CP  (human1, 5 min) — optional alternative
    _p_Deliver_Box1_CP = model.NewBoolVar('Deliver_Box1_CP')
    pr['Deliver_Box1_CP']  = _p_Deliver_Box1_CP
    asg[('Deliver_Box1_CP', 'human1')] = _p_Deliver_Box1_CP
    ts['Deliver_Box1_CP'], te['Deliver_Box1_CP'] = make_iv('Deliver_Box1_CP', 5)
    agent_ivs['human1'].append(
        model.NewOptionalIntervalVar(ts['Deliver_Box1_CP'], 5, te['Deliver_Box1_CP'], _p_Deliver_Box1_CP, 'Deliver_Box1_CP_iv'))

    # Deliver_Box1_HP  (human1, 16 min) — optional alternative
    _p_Deliver_Box1_HP = model.NewBoolVar('Deliver_Box1_HP')
    pr['Deliver_Box1_HP']  = _p_Deliver_Box1_HP
    asg[('Deliver_Box1_HP', 'human1')] = _p_Deliver_Box1_HP
    ts['Deliver_Box1_HP'], te['Deliver_Box1_HP'] = make_iv('Deliver_Box1_HP', 16)
    agent_ivs['human1'].append(
        model.NewOptionalIntervalVar(ts['Deliver_Box1_HP'], 16, te['Deliver_Box1_HP'], _p_Deliver_Box1_HP, 'Deliver_Box1_HP_iv'))

    # Deliver_Box2_CP  (human1, 10 min) — optional alternative
    _p_Deliver_Box2_CP = model.NewBoolVar('Deliver_Box2_CP')
    pr['Deliver_Box2_CP']  = _p_Deliver_Box2_CP
    asg[('Deliver_Box2_CP', 'human1')] = _p_Deliver_Box2_CP
    ts['Deliver_Box2_CP'], te['Deliver_Box2_CP'] = make_iv('Deliver_Box2_CP', 10)
    agent_ivs['human1'].append(
        model.NewOptionalIntervalVar(ts['Deliver_Box2_CP'], 10, te['Deliver_Box2_CP'], _p_Deliver_Box2_CP, 'Deliver_Box2_CP_iv'))

    # Deliver_Box2_HP  (human1, 16 min) — optional alternative
    _p_Deliver_Box2_HP = model.NewBoolVar('Deliver_Box2_HP')
    pr['Deliver_Box2_HP']  = _p_Deliver_Box2_HP
    asg[('Deliver_Box2_HP', 'human1')] = _p_Deliver_Box2_HP
    ts['Deliver_Box2_HP'], te['Deliver_Box2_HP'] = make_iv('Deliver_Box2_HP', 16)
    agent_ivs['human1'].append(
        model.NewOptionalIntervalVar(ts['Deliver_Box2_HP'], 16, te['Deliver_Box2_HP'], _p_Deliver_Box2_HP, 'Deliver_Box2_HP_iv'))

    # ── Direction vars (True = start→end, False = end→start) ──────────
    _dir_Harvest_Row1 = model.NewBoolVar('Harvest_Row1_dir')
    _dir_Harvest_Row2 = model.NewBoolVar('Harvest_Row2_dir')

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
    # Drone_Relay  (drone1, 6 min) — active iff any of ['Deliver_Box1_HP', 'Deliver_Box2_HP'] is active
    _p_Drone_Relay = model.NewBoolVar('Drone_Relay')
    pr['Drone_Relay']  = _p_Drone_Relay
    asg[('Drone_Relay', 'drone1')] = _p_Drone_Relay
    ts['Drone_Relay'], te['Drone_Relay'] = make_iv('Drone_Relay', 6)
    agent_ivs['drone1'].append(
        model.NewOptionalIntervalVar(ts['Drone_Relay'], 6, te['Drone_Relay'], _p_Drone_Relay, 'Drone_Relay_iv'))
    model.AddImplication(_p_Deliver_Box1_HP, _p_Drone_Relay)  # if _p_Deliver_Box1_HP is active, Drone_Relay must run
    model.AddImplication(_p_Deliver_Box2_HP, _p_Drone_Relay)  # if _p_Deliver_Box2_HP is active, Drone_Relay must run
    model.AddBoolOr([_p_Drone_Relay.Not(), _p_Deliver_Box1_HP, _p_Deliver_Box2_HP])
    # ^ Drone_Relay only runs if at least one of ['Deliver_Box1_HP', 'Deliver_Box2_HP'] is active

    # ── Initial positioning (agent start → first task) ─────────────────
    model.Add(ts['Harvest_Row1'] >= 1).OnlyEnforceIf(_dir_Harvest_Row1)

    # ── Dependencies ──────────────────────────────────────────────────
    model.Add(ts['Deliver_Box1'] >= te['Harvest_Row1']).OnlyEnforceIf(_dir_Harvest_Row1)
    model.Add(ts['Deliver_Box1'] >= te['Harvest_Row1']).OnlyEnforceIf(_dir_Harvest_Row1.Not())
    model.Add(ts['Harvest_Row2'] >= te['Deliver_Box1_CP'] + 7).OnlyEnforceIf([_p_Deliver_Box1_CP, _dir_Harvest_Row2])
    model.Add(ts['Harvest_Row2'] >= te['Deliver_Box1_CP'] + 5).OnlyEnforceIf([_p_Deliver_Box1_CP, _dir_Harvest_Row2.Not()])
    model.Add(ts['Harvest_Row2'] >= te['Deliver_Box1_HP'] + 9).OnlyEnforceIf([_p_Deliver_Box1_HP, _dir_Harvest_Row2])
    model.Add(ts['Harvest_Row2'] >= te['Deliver_Box1_HP'] + 8).OnlyEnforceIf([_p_Deliver_Box1_HP, _dir_Harvest_Row2.Not()])
    model.Add(ts['Deliver_Box2'] >= te['Harvest_Row2']).OnlyEnforceIf(_dir_Harvest_Row2)
    model.Add(ts['Deliver_Box2'] >= te['Harvest_Row2']).OnlyEnforceIf(_dir_Harvest_Row2.Not())
    model.Add(ts['Drone_Relay'] >= te['Deliver_Box1_HP']).OnlyEnforceIf([_p_Drone_Relay, _p_Deliver_Box1_HP])
    model.Add(ts['Drone_Relay'] >= te['Deliver_Box2_HP']).OnlyEnforceIf([_p_Drone_Relay, _p_Deliver_Box2_HP])
    model.Add(ts['Tractor_Final'] >= te['Deliver_Box1_CP']).OnlyEnforceIf(_p_Deliver_Box1_CP)
    model.Add(ts['Tractor_Final'] >= te['Deliver_Box2_CP']).OnlyEnforceIf(_p_Deliver_Box2_CP)
    model.Add(ts['Tractor_Final'] >= te['Drone_Relay']).OnlyEnforceIf(_p_Drone_Relay)
    model.Add(ts['Deliver_Box1_CP'] >= te['Harvest_Row1'] + 5).OnlyEnforceIf([_p_Deliver_Box1_CP, _dir_Harvest_Row1])
    model.Add(ts['Deliver_Box1_CP'] >= te['Harvest_Row1'] + 6).OnlyEnforceIf([_p_Deliver_Box1_CP, _dir_Harvest_Row1.Not()])
    model.Add(ts['Deliver_Box1_HP'] >= te['Harvest_Row1']).OnlyEnforceIf([_p_Deliver_Box1_HP, _dir_Harvest_Row1])
    model.Add(ts['Deliver_Box1_HP'] >= te['Harvest_Row1'] + 1).OnlyEnforceIf([_p_Deliver_Box1_HP, _dir_Harvest_Row1.Not()])
    model.Add(ts['Deliver_Box2_CP'] >= te['Harvest_Row2']).OnlyEnforceIf([_p_Deliver_Box2_CP, _dir_Harvest_Row2])
    model.Add(ts['Deliver_Box2_CP'] >= te['Harvest_Row2'] + 10).OnlyEnforceIf([_p_Deliver_Box2_CP, _dir_Harvest_Row2.Not()])
    model.Add(ts['Deliver_Box2_HP'] >= te['Harvest_Row2']).OnlyEnforceIf([_p_Deliver_Box2_HP, _dir_Harvest_Row2])
    model.Add(ts['Deliver_Box2_HP'] >= te['Harvest_Row2'] + 10).OnlyEnforceIf([_p_Deliver_Box2_HP, _dir_Harvest_Row2.Not()])

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
    _task_locs    = {'Harvest_Row1': ('l1', 'l2'), 'Harvest_Row2': ('l3', 'l4'), 'Deliver_Box1_CP': ('l5', 'l5'), 'Deliver_Box1_HP': ('l2', 'l6'), 'Deliver_Box2_CP': ('l4', 'l5'), 'Deliver_Box2_HP': ('l4', 'l6'), 'Drone_Relay': ('l6', 'l5'), 'Tractor_Final': ('l5', 'l7')}
    _dir_vars     = {'Harvest_Row1': _dir_Harvest_Row1, 'Harvest_Row2': _dir_Harvest_Row2}
    _agent_init   = {'drone1': 'l6', 'human1': 'l2', 'tractor1': 'l5'}
    _task_intra   = {'Deliver_Box1_HP': ('l2l6', 8), 'Deliver_Box2_CP': ('l4l5', 5), 'Deliver_Box2_HP': ('l4l6', 8), 'Drone_Relay': ('l6l5', 3), 'Harvest_Row1': ('l1l2', 1), 'Harvest_Row2': ('l3l4', 10), 'Tractor_Final': ('l5l7', 15)}
    _agent_paths  = {('human1', 'l1', 'l3'): [('l1', 'l2', 1), ('l2', 'l5', 5), ('l5', 'l3', 7)], ('human1', 'l1', 'l4'): [('l1', 'l2', 1), ('l2', 'l5', 5), ('l5', 'l4', 5)], ('human1', 'l1', 'l5'): [('l1', 'l2', 1), ('l2', 'l5', 5)], ('human1', 'l1', 'l6'): [('l1', 'l2', 1), ('l2', 'l6', 8)], ('human1', 'l2', 'l3'): [('l2', 'l5', 5), ('l5', 'l3', 7)], ('human1', 'l2', 'l4'): [('l2', 'l5', 5), ('l5', 'l4', 5)], ('human1', 'l3', 'l1'): [('l3', 'l5', 7), ('l5', 'l2', 5), ('l2', 'l1', 1)], ('human1', 'l3', 'l2'): [('l3', 'l5', 7), ('l5', 'l2', 5)], ('human1', 'l4', 'l1'): [('l4', 'l5', 5), ('l5', 'l2', 5), ('l2', 'l1', 1)], ('human1', 'l4', 'l2'): [('l4', 'l5', 5), ('l5', 'l2', 5)], ('human1', 'l5', 'l1'): [('l5', 'l2', 5), ('l2', 'l1', 1)], ('human1', 'l5', 'l6'): [('l5', 'l2', 5), ('l2', 'l6', 8)], ('human1', 'l6', 'l1'): [('l6', 'l2', 8), ('l2', 'l1', 1)], ('human1', 'l6', 'l5'): [('l6', 'l2', 8), ('l2', 'l5', 5)]}
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
        prev_e, prev_loc = 0, _agent_init.get(agent_id, "?")
        for s, e, tid in schedule:
            sl, el = _task_locs.get(tid, ("?", "?"))
            dv = _dir_vars.get(tid)
            if dv is not None and not v(dv):
                sl, el = el, sl  # reversed direction
            if s > prev_e and prev_loc != sl:
                hops = _agent_paths.get((agent_id, prev_loc, sl))
                if hops:
                    t = prev_e
                    for h_from, h_to, h_dur in hops:
                        print(f"  [{t:02d}→{t+h_dur:02d}] Travelling  ({h_from} → {h_to})")
                        t += h_dur
                else:
                    print(f"  [{prev_e:02d}→{s:02d}] Travelling  ({prev_loc} → {sl})")
            intra = _task_intra.get(tid)
            intra_str = f" [travel {intra[0]}={intra[1]}]" if intra else ""
            print(f"  [{s:02d}→{e:02d}] {tid}{intra_str}  ({sl} → {el})")
            prev_e, prev_loc = e, el
        print()


if __name__ == '__main__':
    main()