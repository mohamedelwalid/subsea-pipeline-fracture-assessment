# Verification

## Automated checks

Run:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover:

- hydrostatic pressure for the default water depth;
- reproduction of the hand-calculated hoop stress and simplified `K_I`;
- the failed plane-strain-size check for the default case;
- square-root scaling with crack depth;
- zero Mode I opening when external pressure exceeds internal pressure;
- input validation; and
- reproduction of selected toughness-utilisation pressure boundaries.

## Numerical verification still required

The analytical model has not yet been validated against a correct crack-tip FE
solution. Abaqus results will only be compared after seam definition, crack
front construction, local mesh refinement, contour review and mesh convergence
have been documented.

