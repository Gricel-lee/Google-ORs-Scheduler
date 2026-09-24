from ortools.sat.python import cp_model
import os

# ─────────────────────────────────────────────────────────────────────
# Auto-generated CP-SAT solver
# Targets       : ['_Completed']
# Max duration  : 100 min
# Virtual nodes : ['_Completed']  (abstract; resolved by alternatives)
# Derived-opt.  : []  (run only when triggered)
# OR-optional   : ['Harvest_Row1', 'Pickbox_drone_after_human_Row1', 'Pickbox_human_Row1']  (at least one per OR-dep group must run)
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
    agent_ivs = {a: [] for a in ['human1', 'drone']}

    # ── Mandatory concrete tasks ───────────────────────────────────────
    # ── Optional subtasks (concrete alternatives of virtual nodes) ──────
    # Delivered_by_drone_Row1  (drone, 2 min) — optional alternative
    _p_Delivered_by_drone_Row1 = model.new_bool_var('Delivered_by_drone_Row1')
    pr['Delivered_by_drone_Row1']  = _p_Delivered_by_drone_Row1
    asg[('Delivered_by_drone_Row1', 'drone')] = _p_Delivered_by_drone_Row1
    ts['Delivered_by_drone_Row1'], te['Delivered_by_drone_Row1'] = make_iv('Delivered_by_drone_Row1', 2)
    agent_ivs['drone'].append(
        model.new_optional_interval_var(ts['Delivered_by_drone_Row1'], 2, te['Delivered_by_drone_Row1'], _p_Delivered_by_drone_Row1, 'Delivered_by_drone_Row1_iv'))

    # Delivered_by_human_Row1  (human1, 22 min) — optional alternative
    _p_Delivered_by_human_Row1 = model.new_bool_var('Delivered_by_human_Row1')
    pr['Delivered_by_human_Row1']  = _p_Delivered_by_human_Row1
    asg[('Delivered_by_human_Row1', 'human1')] = _p_Delivered_by_human_Row1
    ts['Delivered_by_human_Row1'], te['Delivered_by_human_Row1'] = make_iv('Delivered_by_human_Row1', 22)
    agent_ivs['human1'].append(
        model.new_optional_interval_var(ts['Delivered_by_human_Row1'], 22, te['Delivered_by_human_Row1'], _p_Delivered_by_human_Row1, 'Delivered_by_human_Row1_iv'))

    # ── OR-optional tasks (at least one per OR-dep group must run) ───────
    # Harvest_Row1  (human1, 3 min) — OR-optional
    _p_Harvest_Row1 = model.new_bool_var('Harvest_Row1')
    pr['Harvest_Row1']  = _p_Harvest_Row1
    asg[('Harvest_Row1', 'human1')] = _p_Harvest_Row1
    ts['Harvest_Row1'], te['Harvest_Row1'] = make_iv('Harvest_Row1', 3)
    agent_ivs['human1'].append(
        model.new_optional_interval_var(ts['Harvest_Row1'], 3, te['Harvest_Row1'], _p_Harvest_Row1, 'Harvest_Row1_iv'))

    # Pickbox_drone_after_human_Row1  (drone, 1 min) — OR-optional
    _p_Pickbox_drone_after_human_Row1 = model.new_bool_var('Pickbox_drone_after_human_Row1')
    pr['Pickbox_drone_after_human_Row1']  = _p_Pickbox_drone_after_human_Row1
    asg[('Pickbox_drone_after_human_Row1', 'drone')] = _p_Pickbox_drone_after_human_Row1
    ts['Pickbox_drone_after_human_Row1'], te['Pickbox_drone_after_human_Row1'] = make_iv('Pickbox_drone_after_human_Row1', 1)
    agent_ivs['drone'].append(
        model.new_optional_interval_var(ts['Pickbox_drone_after_human_Row1'], 1, te['Pickbox_drone_after_human_Row1'], _p_Pickbox_drone_after_human_Row1, 'Pickbox_drone_after_human_Row1_iv'))

    # Pickbox_human_Row1  (human1, 4 min) — OR-optional
    _p_Pickbox_human_Row1 = model.new_bool_var('Pickbox_human_Row1')
    pr['Pickbox_human_Row1']  = _p_Pickbox_human_Row1
    asg[('Pickbox_human_Row1', 'human1')] = _p_Pickbox_human_Row1
    ts['Pickbox_human_Row1'], te['Pickbox_human_Row1'] = make_iv('Pickbox_human_Row1', 4)
    agent_ivs['human1'].append(
        model.new_optional_interval_var(ts['Pickbox_human_Row1'], 4, te['Pickbox_human_Row1'], _p_Pickbox_human_Row1, 'Pickbox_human_Row1_iv'))

    # ── Direction vars (True = start→end, False = end→start) ──────────
    _dir_Harvest_Row1 = model.new_bool_var('Harvest_Row1_dir')

    # ── Virtual nodes (canonical vars bound to whichever alternative runs) ─
    # _Completed  → exactly one of ['Delivered_by_drone_Row1', 'Delivered_by_human_Row1']
    ts['_Completed'] = model.new_int_var(0, horizon, '_Completed_s')
    te['_Completed'] = model.new_int_var(0, horizon, '_Completed_e')
    pr['_Completed']  = model.new_bool_var('_Completed_active')
    model.add_exactly_one([_p_Delivered_by_drone_Row1, _p_Delivered_by_human_Row1])
    model.add(pr['_Completed'] == 1)
    model.add(ts['_Completed'] == ts['Delivered_by_drone_Row1']).OnlyEnforceIf(_p_Delivered_by_drone_Row1)
    model.add(te['_Completed'] == te['Delivered_by_drone_Row1']).OnlyEnforceIf(_p_Delivered_by_drone_Row1)
    model.add(ts['_Completed'] == ts['Delivered_by_human_Row1']).OnlyEnforceIf(_p_Delivered_by_human_Row1)
    model.add(te['_Completed'] == te['Delivered_by_human_Row1']).OnlyEnforceIf(_p_Delivered_by_human_Row1)

    # ── Initial positioning (agent start → first task) ─────────────────
    model.add(ts['Harvest_Row1'] >= 1).only_enforce_if([_p_Harvest_Row1, _dir_Harvest_Row1])
    model.add(ts['Pickbox_drone_after_human_Row1'] >= 1).only_enforce_if(_p_Pickbox_drone_after_human_Row1)

    # ── Dependencies ──────────────────────────────────────────────────
    model.add_implication(_p_Delivered_by_human_Row1, _p_Harvest_Row1)
    model.add(ts['Delivered_by_human_Row1'] >= te['Harvest_Row1']).only_enforce_if([_dir_Harvest_Row1, _p_Harvest_Row1, _p_Delivered_by_human_Row1])
    model.add(ts['Delivered_by_human_Row1'] >= te['Harvest_Row1'] + 1).only_enforce_if([~_dir_Harvest_Row1, _p_Harvest_Row1, _p_Delivered_by_human_Row1])
    model.add_implication(_p_Delivered_by_drone_Row1, _p_Pickbox_drone_after_human_Row1)
    model.add(ts['Delivered_by_drone_Row1'] >= te['Pickbox_drone_after_human_Row1']).only_enforce_if([_p_Pickbox_drone_after_human_Row1, _p_Delivered_by_drone_Row1])
    model.add_implication(_p_Pickbox_human_Row1, _p_Harvest_Row1)
    model.add(ts['Pickbox_human_Row1'] >= te['Harvest_Row1']).only_enforce_if([_dir_Harvest_Row1, _p_Harvest_Row1, _p_Pickbox_human_Row1])
    model.add(ts['Pickbox_human_Row1'] >= te['Harvest_Row1'] + 1).only_enforce_if([~_dir_Harvest_Row1, _p_Harvest_Row1, _p_Pickbox_human_Row1])
    model.add_implication(_p_Pickbox_drone_after_human_Row1, _p_Pickbox_human_Row1)
    model.add(ts['Pickbox_drone_after_human_Row1'] >= te['Pickbox_human_Row1']).only_enforce_if([_p_Pickbox_human_Row1, _p_Pickbox_drone_after_human_Row1])

    # ── Pairwise travel (same-agent, no dep ordering) ────────────────
    # pairwise travel: Delivered_by_human_Row1 ↔ Pickbox_human_Row1 (human1)
    _ord_Delivered_by_human_Row1_Pickbox_human_Row1 = model.new_bool_var('Delivered_by_human_Row1_before_Pickbox_human_Row1')
    model.add(ts['Pickbox_human_Row1'] >= te['Delivered_by_human_Row1'] + 2).only_enforce_if([_ord_Delivered_by_human_Row1_Pickbox_human_Row1, _p_Delivered_by_human_Row1, _p_Pickbox_human_Row1])
    model.add(ts['Delivered_by_human_Row1'] >= te['Pickbox_human_Row1'] + 2).only_enforce_if([~_ord_Delivered_by_human_Row1_Pickbox_human_Row1, _p_Delivered_by_human_Row1, _p_Pickbox_human_Row1])

    # ── Agent no-overlap ──────────────────────────────────────────────
    for agent_id, ivs in agent_ivs.items():
        if len(ivs) > 1:
            model.add_no_overlap(ivs)

    # ── Objective: minimise completion of target tasks ────────────────
    model.minimize(te['_Completed'])

    # ── Solve ─────────────────────────────────────────────────────────
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 4
    status = solver.solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("No solution found within constraints.")
        return

    v = solver.value
    print(f"Solution — makespan: {int(solver.objective_value)} min\n")

    virtual_nodes = ['_Completed']
    _task_locs    = {'Harvest_Row1': ('l1', 'l2'), 'Pickbox_human_Row1': ('l2', 'l3'), 'Pickbox_drone_after_human_Row1': ('l3', 'l4'), 'Delivered_by_human_Row1': ('l2', 'l4'), 'Delivered_by_drone_Row1': ('l4', 'l4')}
    _dir_vars     = {'Harvest_Row1': _dir_Harvest_Row1}
    _agent_init   = {'drone': 'l2', 'human1': 'l2'}
    _task_intra   = {'Delivered_by_human_Row1': ('l2l4', 2), 'Harvest_Row1': ('l1l2', 1), 'Pickbox_drone_after_human_Row1': ('l3l4', 1), 'Pickbox_human_Row1': ('l2l3', 2)}
    _agent_paths  = {('drone', 'l2', 'l4'): [('l2', 'l1', 1), ('l1', 'l4', 1)], ('drone', 'l4', 'l2'): [('l4', 'l1', 1), ('l1', 'l2', 1)], ('human1', 'l2', 'l3'): [('l2', 'l1', 1), ('l1', 'l3', 1)], ('human1', 'l2', 'l4'): [('l2', 'l1', 1), ('l1', 'l4', 1)], ('human1', 'l3', 'l2'): [('l3', 'l1', 1), ('l1', 'l2', 1)], ('human1', 'l4', 'l2'): [('l4', 'l1', 1), ('l1', 'l2', 1)]}
    plan_lines = []
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
                        plan_lines.append(f"    move({agent_id}, {h_from}, {h_to}) [{t:02d}, {t+h_dur:02d}]")
                        t += h_dur
                else:
                    print(f"  [{prev_e:02d}→{s:02d}] Travelling  ({prev_loc} → {sl})")
                    plan_lines.append(f"    move({agent_id}, {prev_loc}, {sl}) [{prev_e:02d}, {s:02d}]")
            intra = _task_intra.get(tid)
            intra_str = f" [task required distance {intra[1]}]" if intra else ""
            print(f"  [{s:02d}→{e:02d}] {tid} ({sl} → {el}) {intra_str}")
            plan_lines.append(f"    dotask({agent_id}, {tid}, {sl}, {el}) [{s:02d}, {e:02d}]")
            prev_e, prev_loc = e, el
        print()

    plan_path = os.path.splitext(os.path.abspath(__file__))[0] + "_plan.txt"
    with open(plan_path, "w") as f:
        f.write("SequentialPlan:\n" + "\n".join(plan_lines) + "\n")
    print(f"Plan written to: {plan_path}")


if __name__ == '__main__':
    main()