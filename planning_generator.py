#!/usr/bin/env python3
"""
planning_generator.py
Reads a planning-problem JSON and emits a runnable CP-SAT solver.

Usage:
    python planning_generator.py example.json [output_solver.py]

The generator handles three kinds of task_graph nodes:

  Concrete    — task ID matches an agent's task list; directly schedulable.
  Virtual     — abstract node whose concrete variants share its name as a
                prefix (e.g. "Deliver_Box1" is virtual; "Deliver_Box1_CP"
                and "Deliver_Box1_HP" are its concrete alternatives).
                Exactly one alternative runs.
  Derived-optional — a concrete task whose OR-dependencies are all optional
                (e.g. Drone_Relay).  Its presence is derived from whether
                at least one of those deps is active.

Constraints enforced
--------------------
  AND deps  : task starts after ALL listed predecessors finish.
  OR deps   : task starts after AT LEAST ONE listed predecessor finishes.
  No-overlap: each agent does at most one task at a time.
  max_duration: hard upper bound on the makespan.

Objective: minimise completion time of tasks_to_be_completed.
"""

import json
import sys
from collections import defaultdict


# ── Helpers ───────────────────────────────────────────────────────────────────

def load(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def safe(s: str) -> str:
    """Make s usable as a Python variable-name segment."""
    for ch in '-. ':
        s = s.replace(ch, '_')
    return s


# ── Problem parsing ───────────────────────────────────────────────────────────

def parse_agents(agents_raw: list) -> tuple[dict, dict]:
    """
    Returns:
      task_to_agents : {task_id: [(agent_id, duration)]}
      agent_travel   : {agent_id: {path_id: duration}}
    """
    task_to_agents: dict = defaultdict(list)
    agent_travel: dict = {}
    for a in agents_raw:
        agent_travel[a['id']] = {tr['id']: tr['duration'] for tr in a.get('travel', [])}
        for t in a.get('tasks', []):
            mv = t.get('metric_values', {})
            dur = mv.get('duration') or mv.get('duration_direct') or 0
            task_to_agents[t['id']].append((a['id'], int(dur)))
    return dict(task_to_agents), agent_travel


def collect_required(task_graph: dict, targets: list) -> set:
    """Walk dependency graph backwards from targets."""
    required: set = set()
    def visit(tid):
        if tid in required:
            return
        required.add(tid)
        for dep in task_graph.get(tid, {}).get('depends_on', []):
            visit(dep)
    for t in targets:
        visit(t)
    return required


def find_subtasks(virtual_id: str, concrete_set: set) -> list:
    """Concrete tasks whose IDs start with virtual_id + '_'."""
    return sorted(t for t in concrete_set if t.startswith(virtual_id + '_'))


def classify_nodes(required: set, task_to_agents: dict, task_graph: dict) -> tuple[set, set, set]:
    """
    Returns (concrete, virtual, derived_optional).

    derived_optional: concrete tasks whose OR-deps are all optional subtasks
    (e.g. Drone_Relay — only needed when HP deliveries happen).
    """
    concrete = required & set(task_to_agents)
    virtual  = required - concrete

    # Build set of all optional subtasks (concrete alternatives of virtual nodes)
    optional_subs: set = set()
    for vid in virtual:
        optional_subs.update(find_subtasks(vid, concrete))

    # A concrete task is "derived-optional" if ALL its deps are optional subtasks
    # (meaning the task only needs to run when those optional predecessors run).
    derived_optional: set = set()
    for tid in concrete - optional_subs:
        node = task_graph.get(tid, {})
        deps = node.get('depends_on', [])
        if deps and all(d in optional_subs for d in deps):
            derived_optional.add(tid)

    return concrete, virtual, derived_optional


# ── Code generation ───────────────────────────────────────────────────────────

def augment_task_graph(task_graph: dict, task_to_agents: dict) -> dict:
    """
    Concrete subtasks of virtual nodes inherit their parent's dependencies
    when they have no entry of their own in the task_graph.

    Example: if task_graph has "Deliver_Box1" -> depends_on ["Harvest_Row1"]
    and concrete agents can perform "Deliver_Box1_CP" and "Deliver_Box1_HP",
    both subtasks get depends_on ["Harvest_Row1"] added to the graph so
    collect_required can reach the harvest tasks from the target chain.
    """
    augmented = {k: dict(v) for k, v in task_graph.items()}  # shallow copy
    for node_id, node in task_graph.items():
        subs = find_subtasks(node_id, set(task_to_agents))
        for st in subs:
            if st not in augmented:
                augmented[st] = {
                    'depends_on':      list(node.get('depends_on', [])),
                    'dependency_type': node.get('dependency_type', 'AND'),
                }
    return augmented


def generate(data: dict) -> str:
    agents_raw  = data['agents']
    task_graph  = data.get('task_graph', {})
    constraints = data.get('constraints', {})
    max_dur     = int(constraints.get('max_duration', 300))
    targets     = constraints.get('tasks_to_be_completed', [])

    task_to_agents, agent_travel = parse_agents(agents_raw)
    agent_ids   = [a['id'] for a in agents_raw]

    # Augment task_graph so concrete subtasks inherit virtual-parent deps,
    # allowing collect_required to reach the full dependency chain.
    task_graph = augment_task_graph(task_graph, task_to_agents)

    required = collect_required(task_graph, targets)

    # Pull virtual parent nodes into required whenever a concrete subtask is already there.
    # (e.g. Tractor_Final depends directly on Deliver_Box2_CP, so Deliver_Box2 is never
    #  visited by collect_required; but it must still be classified as virtual.)
    virtual_nodes_in_graph = {nid for nid in task_graph if nid not in task_to_agents}
    for tid in list(required):
        if tid in task_to_agents:
            for vid in virtual_nodes_in_graph:
                if tid.startswith(vid + '_'):
                    required.add(vid)

    concrete, virtual, derived_optional = classify_nodes(required, task_to_agents, task_graph)

    # Subtask relationships
    subtask_map: dict = {v: find_subtasks(v, concrete) for v in virtual}
    belongs_to:  dict = {s: v for v, subs in subtask_map.items() for s in subs}
    optional_subs = set(belongs_to)          # subtasks of virtual nodes
    mandatory_concrete = concrete - optional_subs - derived_optional

    # ── Emit code ─────────────────────────────────────────────────────────────
    L: list = []
    def w(line: str = ''):
        L.append(line)

    w('from ortools.sat.python import cp_model')
    w()
    w('# ─────────────────────────────────────────────────────────────────────')
    w('# Auto-generated CP-SAT solver')
    w(f'# Targets       : {targets}')
    w(f'# Max duration  : {max_dur} min')
    w(f'# Virtual nodes : {sorted(virtual)}  (abstract; resolved by alternatives)')
    w(f'# Derived-opt.  : {sorted(derived_optional)}  (run only when triggered)')
    w('# ─────────────────────────────────────────────────────────────────────')
    w()
    w()
    w('def main():')
    w('    model = cp_model.CpModel()')
    w(f'    horizon = {max_dur}')
    w()
    w('    def make_iv(name, dur):')
    w('        s = model.NewIntVar(0, horizon, name + "_s")')
    w('        e = model.NewIntVar(0, horizon, name + "_e")')
    w('        model.Add(e == s + dur)')
    w('        return s, e')
    w()
    w('    ts  = {}   # ts[task_id]              -> start IntVar')
    w('    te  = {}   # te[task_id]              -> end   IntVar')
    w('    pr  = {}   # pr[task_id]              -> BoolVar | 1 (presence/active)')
    w('    asg = {}   # asg[(task_id, agent_id)] -> BoolVar | 1')
    w(f'    agent_ivs = {{a: [] for a in {agent_ids!r}}}')
    w()

    # ── Mandatory concrete tasks ───────────────────────────────────────────────
    w('    # ── Mandatory concrete tasks ───────────────────────────────────────')
    for tid in sorted(mandatory_concrete):
        capable = task_to_agents[tid]
        if len(capable) == 1:
            agent_id, dur = capable[0]
            w(f'    # {tid}  ({agent_id}, {dur} min)')
            w(f'    ts[{tid!r}], te[{tid!r}] = make_iv({tid!r}, {dur})')
            w(f'    pr[{tid!r}]  = 1')
            w(f'    asg[({tid!r}, {agent_id!r})] = 1')
            w(f'    agent_ivs[{agent_id!r}].append(')
            w(f'        model.NewIntervalVar(ts[{tid!r}], {dur}, te[{tid!r}], {(tid+"_iv")!r}))')
        else:
            agent_names = [a for a, _ in capable]
            w(f'    # {tid}  (agent choice: {agent_names})')
            w(f'    ts[{tid!r}] = model.NewIntVar(0, horizon, {(tid+"_s")!r})')
            w(f'    te[{tid!r}] = model.NewIntVar(0, horizon, {(tid+"_e")!r})')
            w(f'    pr[{tid!r}]  = 1')
            presences = []
            for agent_id, dur in capable:
                p = f'_p_{safe(tid)}_{safe(agent_id)}'
                w(f'    {p} = model.NewBoolVar({(tid+"_"+agent_id)!r})')
                w(f'    asg[({tid!r}, {agent_id!r})] = {p}')
                w(f'    _s, _e = make_iv({(tid+"_"+agent_id)!r}, {dur})')
                w(f'    model.Add(ts[{tid!r}] == _s).OnlyEnforceIf({p})')
                w(f'    model.Add(te[{tid!r}] == _e).OnlyEnforceIf({p})')
                w(f'    agent_ivs[{agent_id!r}].append(')
                w(f'        model.NewOptionalIntervalVar(_s, {dur}, _e, {p}, {(tid+"_"+agent_id+"_iv")!r}))')
                presences.append(p)
            w(f'    model.AddExactlyOne([{", ".join(presences)}])')
        w()

    # ── Optional subtasks (concrete alternatives of virtual nodes) ─────────────
    w('    # ── Optional subtasks (concrete alternatives of virtual nodes) ──────')
    for tid in sorted(optional_subs):
        capable = task_to_agents[tid]
        agent_id, dur = capable[0]   # always single-agent for this problem
        p = f'_p_{safe(tid)}'
        w(f'    # {tid}  ({agent_id}, {dur} min) — optional alternative')
        w(f'    {p} = model.NewBoolVar({tid!r})')
        w(f'    pr[{tid!r}]  = {p}')
        w(f'    asg[({tid!r}, {agent_id!r})] = {p}')
        w(f'    ts[{tid!r}], te[{tid!r}] = make_iv({tid!r}, {dur})')
        w(f'    agent_ivs[{agent_id!r}].append(')
        w(f'        model.NewOptionalIntervalVar(ts[{tid!r}], {dur}, te[{tid!r}], {p}, {(tid+"_iv")!r}))')
        w()

    # ── Virtual nodes (bind canonical vars to active alternative) ─────────────
    if virtual:
        w('    # ── Virtual nodes (canonical vars bound to whichever alternative runs) ─')
        for vid in sorted(virtual):
            subs = subtask_map.get(vid, [])
            if not subs:
                w(f'    # WARNING: {vid!r} — no concrete alternatives found, skipping')
                continue
            w(f'    # {vid}  → exactly one of {subs}')
            w(f'    ts[{vid!r}] = model.NewIntVar(0, horizon, {(vid+"_s")!r})')
            w(f'    te[{vid!r}] = model.NewIntVar(0, horizon, {(vid+"_e")!r})')
            w(f'    pr[{vid!r}]  = model.NewBoolVar({(vid+"_active")!r})')
            plist = [f'_p_{safe(s)}' for s in subs]
            w(f'    model.AddExactlyOne([{", ".join(plist)}])')
            w(f'    model.Add(pr[{vid!r}] == 1)')   # virtual node is always "done" (one alt runs)
            for st in subs:
                p = f'_p_{safe(st)}'
                w(f'    model.Add(ts[{vid!r}] == ts[{st!r}]).OnlyEnforceIf({p})')
                w(f'    model.Add(te[{vid!r}] == te[{st!r}]).OnlyEnforceIf({p})')
            w()

    # ── Derived-optional tasks (e.g. Drone_Relay) ─────────────────────────────
    if derived_optional:
        w('    # ── Derived-optional tasks (presence driven by OR-deps) ────────────')
        for tid in sorted(derived_optional):
            capable = task_to_agents[tid]
            agent_id, dur = capable[0]
            node = task_graph.get(tid, {})
            deps = node.get('depends_on', [])
            dep_presences = [f'_p_{safe(d)}' for d in deps]
            p = f'_p_{safe(tid)}'
            w(f'    # {tid}  ({agent_id}, {dur} min) — active iff any of {deps} is active')
            w(f'    {p} = model.NewBoolVar({tid!r})')
            w(f'    pr[{tid!r}]  = {p}')
            w(f'    asg[({tid!r}, {agent_id!r})] = {p}')
            w(f'    ts[{tid!r}], te[{tid!r}] = make_iv({tid!r}, {dur})')
            w(f'    agent_ivs[{agent_id!r}].append(')
            w(f'        model.NewOptionalIntervalVar(ts[{tid!r}], {dur}, te[{tid!r}], {p}, {(tid+"_iv")!r}))')
            # presence ↔ (dep1 OR dep2 OR ...)
            for dp in dep_presences:
                w(f'    model.AddImplication({dp}, {p})  # if {dp} is active, {tid} must run')
            # If {tid} runs, at least one dep must be active (NOT presence → impossible, so: presence → any dep)
            w(f'    model.AddBoolOr([{p}.Not(), {", ".join(dep_presences)}])')
            w(f'    # ^ {tid} only runs if at least one of {[d for d in deps]} is active')
            w()

    # ── Dependencies ──────────────────────────────────────────────────────────
    w('    # ── Dependencies ──────────────────────────────────────────────────')
    for tid, node in task_graph.items():
        if tid not in required:
            continue
        deps = [d for d in node.get('depends_on', []) if d in required]
        if not deps:
            continue
        dep_type = node.get('dependency_type', 'AND')
        is_opt   = tid in optional_subs or tid in derived_optional
        p_tid    = f'pr[{tid!r}]' if not is_opt else f'_p_{safe(tid)}'

        if dep_type == 'AND':
            for dep in deps:
                dep_is_opt = dep in optional_subs or dep in derived_optional
                dep_p = f'_p_{safe(dep)}'
                w(f'    # {tid} starts after {dep}  (AND{"_IF_ACTIVE" if dep_is_opt else ""})')
                guards = []
                if is_opt:
                    guards.append(p_tid)
                if dep_is_opt:
                    guards.append(dep_p)
                if len(guards) == 0:
                    w(f'    model.Add(ts[{tid!r}] >= te[{dep!r}])')
                elif len(guards) == 1:
                    w(f'    model.Add(ts[{tid!r}] >= te[{dep!r}]).OnlyEnforceIf({guards[0]})')
                else:
                    w(f'    model.Add(ts[{tid!r}] >= te[{dep!r}]).OnlyEnforceIf([{", ".join(guards)}])')
        else:
            bvars = []
            for dep in deps:
                bv = f'_dep_{safe(tid)}_{safe(dep)}'
                dep_is_opt = dep in optional_subs or dep in derived_optional
                dep_p = f'_p_{safe(dep)}'
                w(f'    {bv} = model.NewBoolVar({(tid+"_after_"+dep)!r})')
                if is_opt:
                    w(f'    model.Add(ts[{tid!r}] >= te[{dep!r}]).OnlyEnforceIf([{bv}, {p_tid}])')
                else:
                    w(f'    model.Add(ts[{tid!r}] >= te[{dep!r}]).OnlyEnforceIf({bv})')
                if dep_is_opt:
                    # Guard: solver may only "wait for dep" when dep is actually active.
                    # Without this, an inactive dep's ts/te=0 trivially satisfies the constraint.
                    w(f'    model.AddImplication({bv}, {dep_p})')
                bvars.append(bv)
            if is_opt:
                w(f'    model.AddBoolOr([{", ".join(bvars)}, {p_tid}.Not()])')
                w(f'    # ^ {tid}: when active, must start after at least one ACTIVE dep in {deps}')
            else:
                w(f'    model.AddBoolOr([{", ".join(bvars)}])')
                w(f'    # ^ {tid} starts after ANY active dep in {deps}')
    w()

    # ── Agent no-overlap ──────────────────────────────────────────────────────
    w('    # ── Agent no-overlap ──────────────────────────────────────────────')
    w('    for agent_id, ivs in agent_ivs.items():')
    w('        if len(ivs) > 1:')
    w('            model.AddNoOverlap(ivs)')
    w()

    # ── Objective ─────────────────────────────────────────────────────────────
    w('    # ── Objective: minimise completion of target tasks ────────────────')
    valid_targets = [t for t in targets if t in required]
    if len(valid_targets) == 1:
        w(f'    model.Minimize(te[{valid_targets[0]!r}])')
    elif valid_targets:
        w('    makespan = model.NewIntVar(0, horizon, "makespan")')
        w(f'    model.AddMaxEquality(makespan, [{", ".join(f"te[{t!r}]" for t in valid_targets)}])')
        w('    model.Minimize(makespan)')
    w()

    # ── Solve ─────────────────────────────────────────────────────────────────
    w('    # ── Solve ─────────────────────────────────────────────────────────')
    w('    solver = cp_model.CpSolver()')
    w('    solver.parameters.num_search_workers = 4')
    w('    status = solver.Solve(model)')
    w()
    w('    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:')
    w('        print("No solution found within constraints.")')
    w('        return')
    w()
    w('    v = solver.Value')
    w(f'    print(f"Solution — makespan: {{int(solver.ObjectiveValue())}} min\\n")')
    w()
    w(f'    virtual_nodes = {sorted(virtual)!r}')
    w('    for agent_id in agent_ivs:')
    w('        schedule = []')
    w('        for (tid, aid), presence in asg.items():')
    w('            if aid != agent_id or tid in virtual_nodes:')
    w('                continue')
    w('            active = presence if isinstance(presence, int) else v(presence)')
    w('            if active:')
    w('                schedule.append((v(ts[tid]), v(te[tid]), tid))')
    w('        if not schedule:')
    w('            continue')
    w('        schedule.sort()')
    w('        print(f"=== {agent_id} ===")')
    w('        for s, e, tid in schedule:')
    w('            print(f"  [{s:02d}→{e:02d}] {tid}")')
    w('        print()')
    w()
    w()
    w("if __name__ == '__main__':")
    w('    main()')

    return '\n'.join(L)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(f'Usage: python {sys.argv[0]} <problem.json> [output.py]')
        sys.exit(1)

    in_path  = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else 'generated_solver.py'

    data = load(in_path)
    code = generate(data)

    with open(out_path, 'w') as f:
        f.write(code)

    print(f'Solver written to  : {out_path}')
    print(f'Run with           : python {out_path}')


if __name__ == '__main__':
    main()
