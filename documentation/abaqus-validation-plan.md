# Abaqus validation plan

The original course model did not produce a valid fracture result because the
intended crack faces remained connected. Negative contour-integral output from
that model is not used as analytical validation.

## Required rebuild

1. Create the pipe or a justified symmetry segment using the documented
   geometry and material properties.
2. Define a correctly shaped longitudinal surface crack.
3. Partition the crack region and create separate crack faces using a seam or
   another documented Abaqus fracture method.
4. Define the crack front and crack-extension direction.
5. Apply internal and external pressure with boundary conditions that avoid
   rigid-body motion without over-constraining radial expansion.
6. Use quadratic solid elements and a refined crack-front mesh suitable for
   contour-integral evaluation.
7. Request multiple `J` or stress-intensity contours along the crack front.
8. Check that the selected contours are positive, stable and sufficiently
   independent of the innermost contour.
9. Repeat the solution with at least three local mesh densities.
10. Compare converged numerical results with an analytical reference while
    documenting the limitations of the constant geometry factor.

## Evidence to export

- geometry and crack-location view;
- seam/crack-front definition;
- boundary conditions and pressure loads;
- global and crack-front mesh views;
- stress contour with units and legend;
- contour-integral result table or path plot;
- mesh-convergence table and plot;
- comparison between analytical and numerical results;
- Abaqus `.cae` and `.inp` files.

The potentially large `.odb` file should normally remain outside GitHub. A
small CSV export of the reviewed contour results is preferable.

