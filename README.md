# calcguard

Executable physics assertions for engineering calculation programs.

Six defects in a cold-formed-steel truss engine passed a 1277-test suite.
Two were unconservative and in the shipped design path. Every one was caught
by an independent tool or a violated invariant — none by the tests.

calcguard turns those invariants into assertions that run in CI.

## Install

    pip install -e ~/projects/calcguard

## Use

    from calcguard import assert_equilibrium, assert_matches_closed_form

    assert_equilibrium(MyAdapter(model, result))
    assert_matches_closed_form(mid_moment, w * L**2 / 8, cite="wL^2/8")

Tier 1 needs nothing. Tier 2 needs a ~20-line adapter. Tier 3 compares
against an external reference, reconciling sign convention and units.

## The one to start with

`assert_equilibrium`. It catches three of the six on its own, because
neither a sign error nor a stale length nor a force at the wrong end can
satisfy it.
