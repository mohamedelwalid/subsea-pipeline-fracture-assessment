# Analytical basis

## Loading model

The pipe is screened using internal pressure reduced by hydrostatic external
pressure at the specified water depth. Thin-wall hoop stress is evaluated at
the mean radius.

The default geometry has an inner-radius-to-thickness ratio of 10, which is the
selected lower boundary for the thin-wall approximation in this educational
model.

## Stress-intensity approximation

Mode I stress intensity is estimated using:

```text
K_I = Y * sigma_h * sqrt(pi * a)
```

The constant geometry factor `Y = 1.12` is retained from the original course
calculation. It is useful for demonstrating sensitivity to stress and crack
depth but is not a validated solution for the full curved-pipe surface-crack
geometry.

## Plane-strain size screening

The minimum characteristic dimension is estimated from:

```text
2.5 * (K_IC / sigma_y)^2
```

For the default values, the result is approximately 30.86 mm. The wall
thickness and remaining ligament exceed this value, but the assumed 20 mm crack
dimension does not. The plane-strain-size check therefore fails in the current
implementation.

## Interpretation

`K_I / K_IC` is presented as a sensitivity and utilisation indicator. It must
not be interpreted as a formal acceptance assessment because the geometry
factor, toughness applicability and omitted failure modes have not been
validated for a real component.

