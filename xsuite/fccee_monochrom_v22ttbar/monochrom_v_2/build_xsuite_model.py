import numpy as np
import xtrack as xt
import xdeps as xd

from cpymad.madx import Madx

fname = 'ring_monochromv2'
pc_gev = 62.5

mad = Madx()
mad.call('/Users/zhang/Workspaces/monochromatization/xsuite/fcc_v22_t/seq/' + fname + '.seq')
mad.beam(particle='positron', pc=pc_gev)
mad.use('monolattice_vertical')

mad.call('install_wigglers.madx')
mad.input("exec, define_wigglers_as_multipoles()")
mad.input("exec, install_wigglers()")
mad.use('monolattice_vertical')

line_thick = xt.Line.from_madx_sequence(mad.sequence.monolattice_vertical, allow_thick=True,
                                  deferred_expressions=True)
line_thick.particle_ref = xt.Particles(mass0=xt.ELECTRON_MASS_EV,
                                 gamma0=mad.sequence.monolattice_vertical.beam.gamma)
line_thick.build_tracker()
tw_thick_no_rad = line_thick.twiss(method='4d')

line = line_thick.copy()
Strategy = xt.slicing.Strategy
Teapot = xt.slicing.Teapot
slicing_strategies = [
    Strategy(slicing=Teapot(1)),  # Default catch-all as in MAD-X
    Strategy(slicing=Teapot(3), element_type=xt.Bend),
    Strategy(slicing=Teapot(3), element_type=xt.CombinedFunctionMagnet),
    # Strategy(slicing=Teapot(50), element_type=xt.Quadrupole), # Starting point
    Strategy(slicing=Teapot(5), name=r'^qf.*'),
    Strategy(slicing=Teapot(5), name=r'^qd.*'),
    Strategy(slicing=Teapot(5), name=r'^qfg.*'),
    Strategy(slicing=Teapot(5), name=r'^qdg.*'),
    Strategy(slicing=Teapot(5), name=r'^ql.*'),
    Strategy(slicing=Teapot(5), name=r'^qs.*'),
    Strategy(slicing=Teapot(10), name=r'^qb.*'),
    Strategy(slicing=Teapot(10), name=r'^qg.*'),
    Strategy(slicing=Teapot(10), name=r'^qh.*'),
    Strategy(slicing=Teapot(10), name=r'^qi.*'),
    Strategy(slicing=Teapot(10), name=r'^qr.*'),
    Strategy(slicing=Teapot(10), name=r'^qu.*'),
    Strategy(slicing=Teapot(10), name=r'^qy.*'),
    Strategy(slicing=Teapot(50), name=r'^qa.*'),
    Strategy(slicing=Teapot(50), name=r'^qc.*'),
    Strategy(slicing=Teapot(20), name=r'^sy.*'),
]

line.slice_thick_elements(slicing_strategies=slicing_strategies)
line.build_tracker()
tw_thin_before = line.twiss(start='ip.1', end="ip.8", method='4d',
                          init=tw_thick_no_rad.get_twiss_init('ip.8'))

# Compare tunes
print('Before rematching:')

print('Tunes thick model:')
print(tw_thick_no_rad.qx, tw_thick_no_rad.qy)
print('Tunes thin model:')
print(tw_thin_before.mux[-1], tw_thin_before.muy[-1])

print('Beta beating at ips:')
print('H:', np.max(np.abs(
    tw_thin_before.rows['ip.*'].betx / tw_thick_no_rad.rows['ip.*'].betx -1)))
print('V:', np.max(np.abs(
    tw_thin_before.rows['ip.*'].bety / tw_thick_no_rad.rows['ip.*'].bety -1)))

print('Number of elements: ', len(line))
print('\n')

opt1 = line.match(
    only_markers=True,
    method='4d',
    start='ip.1', end='ip.8',
    init=tw_thick_no_rad.get_twiss_init('ip.1'),
    vary=xt.VaryList(['k1qf4', 'k1qf2', 'k1qd3', 'k1qd1',], step=1e-8,
    ),
    targets=[
        xt.TargetSet(at='ip.8', mux=tw_thick_no_rad.qx, muy=tw_thick_no_rad.qy, tol=1e-5),
    ]
)
opt1.solve()

opt2 = line.match(
    only_markers=True,
    method='4d',
    start='ip.1', end='ip.8',
    init='periodic',
    vary=xt.VaryList(['ktskw1l','ktskw1r','k1qrfr1','k1qrfr2','k1qrfr3','k1qrfr4','k1qrfr5','k1qrdr1','k1qrdr2','k1qrdr3','k1qrdr4','k1qrdr5','k1qi2','k1qi3','k1qi4','k1qi5','k1qi6','k1qi7','k1qi8','k1qi9','k1qia','k1qu8','k1qu7','k1qu4','k1qu3','k1qu2','k1qu1',], step=1e-8,
    ),
    targets=[
        xt.TargetSet(at='ip.8', betx=1, bety=0.0016, alfx=0, alfy=0, dx=0, dpx=0, dy=0.002, dpy=0, mux=tw_thick_no_rad.qx, muy=tw_thick_no_rad.qy, tol=1e-5), xt.TargetSet(at='frf.1', alfx=0, alfy=0, tol=1e-5)
    ]
)
opt2.solve()

tw_thin_no_rad = line.twiss(method='4d')

print('After rematching:')
print('Tunes thick model:')
print(tw_thick_no_rad.qx, tw_thick_no_rad.qy)
print('Tunes thin model:')
print(tw_thin_no_rad.qx, tw_thin_no_rad.qy)

print('Beta at ips Thick model:')
print('Betx:', tw_thick_no_rad.rows['ip.4'].betx)
print('Bety:', tw_thick_no_rad.rows['ip.4'].bety)

print('Beta at ips Thin model:')
print('Betx:', tw_thin_no_rad.rows['ip.4'].betx)
print('Bety:', tw_thin_no_rad.rows['ip.4'].bety)

print('Beta beating at ips:')
print('H:', np.max(np.abs(
    tw_thin_no_rad.rows['ip.*'].betx / tw_thick_no_rad.rows['ip.*'].betx -1)))
print('V:', np.max(np.abs(
    tw_thin_no_rad.rows['ip.*'].bety / tw_thick_no_rad.rows['ip.*'].bety -1)))

print('Number of elements: ', len(line))

print('\n Beam parameters at the IPs:')
tw_thin_no_rad.rows['ip.*'].cols['betx alfx bety alfy dx dpx dy dpy'].show()

line.to_json(fname + '_thin.json')
line_thick.to_json(fname + '_thick.json')

