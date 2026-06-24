from ortools.sat.python import cp_model

# ─────────────────────────────────────────────────────────────────────
# Auto-generated CP-SAT solver
# Targets       : ['Harvest_Row3']
# Max duration  : 100 min
# Virtual nodes : []  (abstract; resolved by alternatives)
# Derived-opt.  : []  (run only when triggered)
# OR-optional   : ['Harvest_Row1', 'Harvest_Row2']  (at least one per OR-dep group must run)
# ─────────────────────────────────────────────────────────────────────


def main():
    model = cp_model.CpModel()
    horizon = 100

    def make_iv(name, dur):
        s = model.new_int_var(0, horizon, name + "_s")
        e = model.new_int_var(0, horizon, name + "_e")
        model.add(e == s + dur)
        return s, e

    ts  = {}   # ts[task_id]              -> start IntVar
    te  = {}   # te[task_id]              -> end   IntVar
    pr  = {}   # pr[task_id]              -> BoolVar | 1 (presence/active)
    asg = {}   # asg[(task_id, agent_id)] -> BoolVar | 1
    agent_ivs = {a: [] for a in ['human1', 'human2']}

    # ── Mandatory concrete tasks ───────────────────────────────────────
    # Harvest_Row3  (agent choice: ['human1', 'human2'])
    ts['Harvest_Row3'] = model.new_int_var(0, horizon, 'Harvest_Row3_s')
    te['Harvest_Row3'] = model.new_int_var(0, horizon, 'Harvest_Row3_e')
    pr['Harvest_Row3']  = 1
    _p_Harvest_Row3_human1 = model.new_bool_var('Harvest_Row3_human1')
    asg[('Harvest_Row3', 'human1')] = _p_Harvest_Row3_human1
    _s, _e = make_iv('Harvest_Row3_human1', 5)
    model.add(ts['Harvest_Row3'] == _s).only_enforce_if(_p_Harvest_Row3_human1)
    model.add(te['Harvest_Row3'] == _e).only_enforce_if(_p_Harvest_Row3_human1)
    agent_ivs['human1'].append(
        model.new_optional_interval_var(_s, 5, _e, _p_Harvest_Row3_human1, 'Harvest_Row3_human1_iv'))
    _p_Harvest_Row3_human2 = model.new_bool_var('Harvest_Row3_human2')
    asg[('Harvest_Row3', 'human2')] = _p_Harvest_Row3_human2
    _s, _e = make_iv('Harvest_Row3_human2', 5)
    model.add(ts['Harvest_Row3'] == _s).only_enforce_if(_p_Harvest_Row3_human2)
    model.add(te['Harvest_Row3'] == _e).only_enforce_if(_p_Harvest_Row3_human2)
    agent_ivs['human2'].append(
        model.new_optional_interval_var(_s, 5, _e, _p_Harvest_Row3_human2, 'Harvest_Row3_human2_iv'))
    model.add_exactly_one([_p_Harvest_Row3_human1, _p_Harvest_Row3_human2])

    # ── Optional subtasks (concrete alternatives of virtual nodes) ──────
    # ── OR-optional tasks (at least one per OR-dep group must run) ───────
    # Harvest_Row1  (agent choice: ['human1', 'human2']) — OR-optional
    ts['Harvest_Row1'] = model.new_int_var(0, horizon, 'Harvest_Row1_s')
    te['Harvest_Row1'] = model.new_int_var(0, horizon, 'Harvest_Row1_e')
    _p_Harvest_Row1 = model.new_bool_var('Harvest_Row1')
    pr['Harvest_Row1']  = _p_Harvest_Row1
    _p_Harvest_Row1_human1 = model.new_bool_var('Harvest_Row1_human1')
    asg[('Harvest_Row1', 'human1')] = _p_Harvest_Row1_human1
    _s, _e = make_iv('Harvest_Row1_human1', 3)
    model.add(ts['Harvest_Row1'] == _s).only_enforce_if(_p_Harvest_Row1_human1)
    model.add(te['Harvest_Row1'] == _e).only_enforce_if(_p_Harvest_Row1_human1)
    agent_ivs['human1'].append(
        model.new_optional_interval_var(_s, 3, _e, _p_Harvest_Row1_human1, 'Harvest_Row1_human1_iv'))
    _p_Harvest_Row1_human2 = model.new_bool_var('Harvest_Row1_human2')
    asg[('Harvest_Row1', 'human2')] = _p_Harvest_Row1_human2
    _s, _e = make_iv('Harvest_Row1_human2', 3)
    model.add(ts['Harvest_Row1'] == _s).only_enforce_if(_p_Harvest_Row1_human2)
    model.add(te['Harvest_Row1'] == _e).only_enforce_if(_p_Harvest_Row1_human2)
    agent_ivs['human2'].append(
        model.new_optional_interval_var(_s, 3, _e, _p_Harvest_Row1_human2, 'Harvest_Row1_human2_iv'))
    model.add_at_most_one([_p_Harvest_Row1_human1, _p_Harvest_Row1_human2])
    model.add_implication(_p_Harvest_Row1_human1, _p_Harvest_Row1)
    model.add_implication(_p_Harvest_Row1_human2, _p_Harvest_Row1)
    model.add_bool_or([_p_Harvest_Row1_human1, _p_Harvest_Row1_human2, ~_p_Harvest_Row1])

    # Harvest_Row2  (agent choice: ['human1', 'human2']) — OR-optional
    ts['Harvest_Row2'] = model.new_int_var(0, horizon, 'Harvest_Row2_s')
    te['Harvest_Row2'] = model.new_int_var(0, horizon, 'Harvest_Row2_e')
    _p_Harvest_Row2 = model.new_bool_var('Harvest_Row2')
    pr['Harvest_Row2']  = _p_Harvest_Row2
    _p_Harvest_Row2_human1 = model.new_bool_var('Harvest_Row2_human1')
    asg[('Harvest_Row2', 'human1')] = _p_Harvest_Row2_human1
    _s, _e = make_iv('Harvest_Row2_human1', 11)
    model.add(ts['Harvest_Row2'] == _s).only_enforce_if(_p_Harvest_Row2_human1)
    model.add(te['Harvest_Row2'] == _e).only_enforce_if(_p_Harvest_Row2_human1)
    agent_ivs['human1'].append(
        model.new_optional_interval_var(_s, 11, _e, _p_Harvest_Row2_human1, 'Harvest_Row2_human1_iv'))
    _p_Harvest_Row2_human2 = model.new_bool_var('Harvest_Row2_human2')
    asg[('Harvest_Row2', 'human2')] = _p_Harvest_Row2_human2
    _s, _e = make_iv('Harvest_Row2_human2', 11)
    model.add(ts['Harvest_Row2'] == _s).only_enforce_if(_p_Harvest_Row2_human2)
    model.add(te['Harvest_Row2'] == _e).only_enforce_if(_p_Harvest_Row2_human2)
    agent_ivs['human2'].append(
        model.new_optional_interval_var(_s, 11, _e, _p_Harvest_Row2_human2, 'Harvest_Row2_human2_iv'))
    model.add_at_most_one([_p_Harvest_Row2_human1, _p_Harvest_Row2_human2])
    model.add_implication(_p_Harvest_Row2_human1, _p_Harvest_Row2)
    model.add_implication(_p_Harvest_Row2_human2, _p_Harvest_Row2)
    model.add_bool_or([_p_Harvest_Row2_human1, _p_Harvest_Row2_human2, ~_p_Harvest_Row2])

    # At least one OR-dep of 'Harvest_Row3' must run
    model.add_bool_or([_p_Harvest_Row1, _p_Harvest_Row2])

    # ── Direction vars (True = start→end, False = end→start) ──────────
    _dir_Harvest_Row2 = model.new_bool_var('Harvest_Row2_dir')
    _dir_Harvest_Row3 = model.new_bool_var('Harvest_Row3_dir')

    # ── Initial positioning (agent start → first task) ─────────────────
    model.add(ts['Harvest_Row1'] >= 1).only_enforce_if(_p_Harvest_Row1)
    model.add(ts['Harvest_Row2'] >= 1).only_enforce_if([_p_Harvest_Row2, _dir_Harvest_Row2])
    model.add(ts['Harvest_Row2'] >= 2).only_enforce_if([_p_Harvest_Row2, ~_dir_Harvest_Row2])
    model.add(ts['Harvest_Row1'] >= 1).only_enforce_if(_p_Harvest_Row1)
    model.add(ts['Harvest_Row2'] >= 1).only_enforce_if([_p_Harvest_Row2, _dir_Harvest_Row2])
    model.add(ts['Harvest_Row2'] >= 2).only_enforce_if([_p_Harvest_Row2, ~_dir_Harvest_Row2])

    # ── Dependencies ──────────────────────────────────────────────────
    _dep_Harvest_Row3_Harvest_Row1 = model.new_bool_var('Harvest_Row3_after_Harvest_Row1')
    model.add(ts['Harvest_Row3'] >= te['Harvest_Row1'] + 1).only_enforce_if([_dep_Harvest_Row3_Harvest_Row1, _dir_Harvest_Row3])
    model.add(ts['Harvest_Row3'] >= te['Harvest_Row1'] + 1).only_enforce_if([_dep_Harvest_Row3_Harvest_Row1, ~_dir_Harvest_Row3])
    model.add_implication(_dep_Harvest_Row3_Harvest_Row1, _p_Harvest_Row1)
    _dep_Harvest_Row3_Harvest_Row2 = model.new_bool_var('Harvest_Row3_after_Harvest_Row2')
    model.add(ts['Harvest_Row3'] >= te['Harvest_Row2'] + 1).only_enforce_if([_dep_Harvest_Row3_Harvest_Row2, _dir_Harvest_Row2, _dir_Harvest_Row3])
    model.add(ts['Harvest_Row3'] >= te['Harvest_Row2'] + 1).only_enforce_if([_dep_Harvest_Row3_Harvest_Row2, _dir_Harvest_Row2, ~_dir_Harvest_Row3])
    model.add(ts['Harvest_Row3'] >= te['Harvest_Row2']).only_enforce_if([_dep_Harvest_Row3_Harvest_Row2, ~_dir_Harvest_Row2, _dir_Harvest_Row3])
    model.add(ts['Harvest_Row3'] >= te['Harvest_Row2']).only_enforce_if([_dep_Harvest_Row3_Harvest_Row2, ~_dir_Harvest_Row2, ~_dir_Harvest_Row3])
    model.add_implication(_dep_Harvest_Row3_Harvest_Row2, _p_Harvest_Row2)
    model.add_bool_or([_dep_Harvest_Row3_Harvest_Row1, _dep_Harvest_Row3_Harvest_Row2])
    # ^ Harvest_Row3 starts after ANY active dep in ['Harvest_Row1', 'Harvest_Row2']
    # OR-optional deps only run when chosen by a successor
    model.add_implication(_p_Harvest_Row1, _dep_Harvest_Row3_Harvest_Row1)
    model.add_implication(_p_Harvest_Row2, _dep_Harvest_Row3_Harvest_Row2)


    # ── Pairwise travel (same-agent, no dep ordering) ────────────────
    # pairwise travel: Harvest_Row1 ↔ Harvest_Row2 (human1)
    _ord_Harvest_Row1_Harvest_Row2 = model.new_bool_var('Harvest_Row1_before_Harvest_Row2')
    model.add(ts['Harvest_Row2'] >= te['Harvest_Row1'] + 1).only_enforce_if([_ord_Harvest_Row1_Harvest_Row2, _dir_Harvest_Row2, _p_Harvest_Row1_human1, _p_Harvest_Row2_human1])
    model.add(ts['Harvest_Row2'] >= te['Harvest_Row1'] + 2).only_enforce_if([_ord_Harvest_Row1_Harvest_Row2, ~_dir_Harvest_Row2, _p_Harvest_Row1_human1, _p_Harvest_Row2_human1])
    model.add(ts['Harvest_Row1'] >= te['Harvest_Row2'] + 1).only_enforce_if([~_ord_Harvest_Row1_Harvest_Row2, _dir_Harvest_Row2, _p_Harvest_Row1_human1, _p_Harvest_Row2_human1])
    model.add(ts['Harvest_Row1'] >= te['Harvest_Row2'] + 1).only_enforce_if([~_ord_Harvest_Row1_Harvest_Row2, ~_dir_Harvest_Row2, _p_Harvest_Row1_human1, _p_Harvest_Row2_human1])

    # pairwise travel: Harvest_Row1 ↔ Harvest_Row2 (human2)
    _ord_Harvest_Row1_Harvest_Row2 = model.new_bool_var('Harvest_Row1_before_Harvest_Row2')
    model.add(ts['Harvest_Row2'] >= te['Harvest_Row1'] + 1).only_enforce_if([_ord_Harvest_Row1_Harvest_Row2, _dir_Harvest_Row2, _p_Harvest_Row1_human2, _p_Harvest_Row2_human2])
    model.add(ts['Harvest_Row2'] >= te['Harvest_Row1'] + 2).only_enforce_if([_ord_Harvest_Row1_Harvest_Row2, ~_dir_Harvest_Row2, _p_Harvest_Row1_human2, _p_Harvest_Row2_human2])
    model.add(ts['Harvest_Row1'] >= te['Harvest_Row2'] + 1).only_enforce_if([~_ord_Harvest_Row1_Harvest_Row2, _dir_Harvest_Row2, _p_Harvest_Row1_human2, _p_Harvest_Row2_human2])
    model.add(ts['Harvest_Row1'] >= te['Harvest_Row2'] + 1).only_enforce_if([~_ord_Harvest_Row1_Harvest_Row2, ~_dir_Harvest_Row2, _p_Harvest_Row1_human2, _p_Harvest_Row2_human2])

    # ── Agent no-overlap ──────────────────────────────────────────────
    for agent_id, ivs in agent_ivs.items():
        if len(ivs) > 1:
            model.add_no_overlap(ivs)

    # ── Objective: minimise completion of target tasks ────────────────
    model.minimize(te['Harvest_Row3'])

    # ── Solve ─────────────────────────────────────────────────────────
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 4
    status = solver.solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("No solution found within constraints.")
        return

    v = solver.value
    print(f"Solution — makespan: {int(solver.objective_value)} min\n")

    virtual_nodes = []
    _task_locs    = {'Harvest_Row1': ('l1', 'l2'), 'Harvest_Row2': ('l3', 'l4'), 'Harvest_Row3': ('l3', 'l3')}
    _dir_vars     = {'Harvest_Row2': _dir_Harvest_Row2, 'Harvest_Row3': _dir_Harvest_Row3}
    _agent_init   = {'human1': 'l2', 'human2': 'l2'}
    _task_intra   = {'Harvest_Row1': ('l1l2', 1), 'Harvest_Row2': ('l3l4', 1)}
    _agent_paths  = {('human1', 'l2', 'l4'): [('l2', 'l1', 1), ('l1', 'l4', 1)], ('human1', 'l4', 'l2'): [('l4', 'l1', 1), ('l1', 'l2', 1)], ('human2', 'l2', 'l4'): [('l2', 'l1', 1), ('l1', 'l4', 1)], ('human2', 'l4', 'l2'): [('l4', 'l1', 1), ('l1', 'l2', 1)]}
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
            intra_str = f" [task required distance {intra[1]}]" if intra else ""
            print(f"  [{s:02d}→{e:02d}] {tid} ({sl} → {el}) {intra_str}")
            prev_e, prev_loc = e, el
        print()


if __name__ == '__main__':
    main()