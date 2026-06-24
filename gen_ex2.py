from ortools.sat.python import cp_model

# ─────────────────────────────────────────────────────────────────────
# Auto-generated CP-SAT solver
# Targets       : ['Harvest_Row1', 'Harvest_Row2']
# Max duration  : 100 min
# Virtual nodes : ['Deliver_Box1']  (abstract; resolved by alternatives)
# Derived-opt.  : []  (run only when triggered)
# ─────────────────────────────────────────────────────────────────────


def main():
    model = cp_model.CpModel()
    horizon = 100

    def make_iv(name, dur):
        """
        Create a pair of OR-Tools integer decision variables representing the start and end of an interval.
        Args:
            name (str): Base name for the variables.
            dur (int): Duration of the interval.
        """
        s = model.NewIntVar(0, horizon, name + "_s") # start variable
        e = model.NewIntVar(0, horizon, name + "_e") # end variable
        model.Add(e == s + dur) # constraint: the solver is forced to pick values for s and e s.t. e == s + dur
        return s, e

    ts  = {}   # ts[task_id]              -> start IntVar
    te  = {}   # te[task_id]              -> end   IntVar
    pr  = {}   # pr[task_id]              -> BoolVar | 1 (presence/active)
    asg = {}   # asg[(task_id, agent_id)] -> BoolVar | 1
    agent_ivs = {a: [] for a in ['human1']}

    # ── Mandatory concrete tasks ───────────────────────────────────────
    # Harvest_Row1  (human1, 3 min)
    ts['Harvest_Row1'], te['Harvest_Row1'] = make_iv('Harvest_Row1', 3)
    pr['Harvest_Row1']  = 1
    asg[('Harvest_Row1', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Harvest_Row1'], 3, te['Harvest_Row1'], 'Harvest_Row1_iv'))

    # Harvest_Row2  (human1, 11 min)
    ts['Harvest_Row2'], te['Harvest_Row2'] = make_iv('Harvest_Row2', 11)
    pr['Harvest_Row2']  = 1
    asg[('Harvest_Row2', 'human1')] = 1
    agent_ivs['human1'].append(
        model.NewIntervalVar(ts['Harvest_Row2'], 11, te['Harvest_Row2'], 'Harvest_Row2_iv'))

    # ── Optional subtasks (concrete alternatives of virtual nodes) ──────
    # ── Direction vars (True = start→end, False = end→start) ──────────
    _dir_Harvest_Row1 = model.NewBoolVar('Harvest_Row1_dir')
    _dir_Harvest_Row2 = model.NewBoolVar('Harvest_Row2_dir')

    # ── Virtual nodes (canonical vars bound to whichever alternative runs) ─
    # WARNING: 'Deliver_Box1' — no concrete alternatives found, skipping
    # ── Initial positioning (agent start → first task) ─────────────────
    model.Add(ts['Harvest_Row1'] >= 1).OnlyEnforceIf(_dir_Harvest_Row1)
    model.Add(ts['Harvest_Row2'] >= 1).OnlyEnforceIf(_dir_Harvest_Row2)
    model.Add(ts['Harvest_Row2'] >= 1).OnlyEnforceIf(_dir_Harvest_Row2.Not())

    # ── Dependencies ──────────────────────────────────────────────────

    # ── Pairwise travel (same-agent, no dep ordering) ────────────────
    # pairwise travel: Harvest_Row1 ↔ Harvest_Row2 (human1)
    _ord_Harvest_Row1_Harvest_Row2 = model.NewBoolVar('Harvest_Row1_before_Harvest_Row2')
    model.Add(ts['Harvest_Row2'] >= te['Harvest_Row1'] + 1).OnlyEnforceIf([_ord_Harvest_Row1_Harvest_Row2, _dir_Harvest_Row1, _dir_Harvest_Row2])
    model.Add(ts['Harvest_Row2'] >= te['Harvest_Row1'] + 1).OnlyEnforceIf([_ord_Harvest_Row1_Harvest_Row2, _dir_Harvest_Row1, _dir_Harvest_Row2.Not()])
    model.Add(ts['Harvest_Row2'] >= te['Harvest_Row1'] + 1).OnlyEnforceIf([_ord_Harvest_Row1_Harvest_Row2, _dir_Harvest_Row1.Not(), _dir_Harvest_Row2])
    model.Add(ts['Harvest_Row2'] >= te['Harvest_Row1'] + 1).OnlyEnforceIf([_ord_Harvest_Row1_Harvest_Row2, _dir_Harvest_Row1.Not(), _dir_Harvest_Row2.Not()])
    model.Add(ts['Harvest_Row1'] >= te['Harvest_Row2'] + 1).OnlyEnforceIf([_ord_Harvest_Row1_Harvest_Row2.Not(), _dir_Harvest_Row2, _dir_Harvest_Row1])
    model.Add(ts['Harvest_Row1'] >= te['Harvest_Row2'] + 1).OnlyEnforceIf([_ord_Harvest_Row1_Harvest_Row2.Not(), _dir_Harvest_Row2, _dir_Harvest_Row1.Not()])
    model.Add(ts['Harvest_Row1'] >= te['Harvest_Row2'] + 1).OnlyEnforceIf([_ord_Harvest_Row1_Harvest_Row2.Not(), _dir_Harvest_Row2.Not(), _dir_Harvest_Row1])
    model.Add(ts['Harvest_Row1'] >= te['Harvest_Row2'] + 1).OnlyEnforceIf([_ord_Harvest_Row1_Harvest_Row2.Not(), _dir_Harvest_Row2.Not(), _dir_Harvest_Row1.Not()])

    # ── Agent no-overlap ──────────────────────────────────────────────
    for agent_id, ivs in agent_ivs.items():
        if len(ivs) > 1:
            model.AddNoOverlap(ivs)

    # ── Objective: minimise completion of target tasks ────────────────
    makespan = model.NewIntVar(0, horizon, "makespan")
    model.AddMaxEquality(makespan, [te['Harvest_Row1'], te['Harvest_Row2']])
    model.Minimize(makespan)

    # ── Solve ─────────────────────────────────────────────────────────
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 4
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("No solution found within constraints.")
        return

    v = solver.Value
    print(f"Solution — makespan: {int(solver.ObjectiveValue())} min\n")

    virtual_nodes = ['Deliver_Box1']
    _task_locs    = {'Harvest_Row1': ('l1', 'l2'), 'Harvest_Row2': ('l3', 'l4')}
    _dir_vars     = {'Harvest_Row1': _dir_Harvest_Row1, 'Harvest_Row2': _dir_Harvest_Row2}
    _agent_init   = {'human1': 'l2'}
    _task_intra   = {'Harvest_Row1': ('l1l2', 1), 'Harvest_Row2': ('l3l4', 1)}
    _agent_paths  = {}
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