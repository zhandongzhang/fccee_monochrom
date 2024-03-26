import matplotlib.pyplot as plt
import numpy as np
import xtrack as xt

line = xt.Line.from_json('ring_monochrom2_thin.json')

line.build_tracker()

tw_no_rad = line.twiss(method='4d').to_pandas()
tw_no_rad.to_csv('twiss_no_rad.csv')

line.vars['voltca1'] = 15
line.vars['lagca1'] = 0.43631343868376266

line.configure_radiation(model='mean')
line.compensate_radiation_energy_loss()

tw_rad_wig_off = line.twiss(eneloss_and_damping=True).to_pandas()
tw_rad_wig_off.to_csv('twiss_rad_wig_off.csv')

tw_rad_wig_off = line.twiss(eneloss_and_damping=True)

ex = tw_rad_wig_off.eq_gemitt_x
ey = tw_rad_wig_off.eq_gemitt_y
ez = tw_rad_wig_off.eq_gemitt_zeta
eloss_turn = tw_rad_wig_off.eneloss_turn
alfa = tw_rad_wig_off.momentum_compaction_factor
qs = tw_rad_wig_off.qs
damping_time = 1/(tw_rad_wig_off.damping_constants_s[2])
sigma_z = np.sqrt(tw_rad_wig_off.bets0*ez)
sige = sigma_z*2*np.pi*qs/alfa/tw_rad_wig_off.circumference

print('\n Beam parameters at the IPs:')
tw_rad_wig_off.rows['ip.*'].cols['betx alfx bety alfy dx dpx dy dpy'].show()

with open('performance.txt', 'w') as f:
    f.write('Performance parameters check:')
    f.write('\n @ Emittance:')
    f.write('\nEx: ')
    f.write(str(ex))
    f.write('\nEy: ')
    f.write(str(ey))
    f.write('\nEz: ')
    f.write(str(ez))
    f.write('\n @ Energy loss per turn:\n')
    f.write(str(eloss_turn))
    f.write('\n @ Momentum compaction factor:\n')
    f.write(str(alfa))
    f.write('\n @ Energy spread:\n')
    f.write(str(sige))
    f.write('\n @ Bunch length:\n')
    f.write(str(sigma_z))
    f.write('\n @ Sychrotron tune:\n')
    f.write(str(qs))
    f.write('\n @ Longitudinal damping time:\n')
    f.write(str(damping_time))

fig1 = plt.figure(1, figsize=(6.4, 4.8*1.5))
spbet = plt.subplot(3,1,1)
spco = plt.subplot(3,1,2, sharex=spbet)
spdisp = plt.subplot(3,1,3, sharex=spbet)

spbet.plot(tw_rad_wig_off ['s'], tw_rad_wig_off ['betx'])
spbet.plot(tw_rad_wig_off ['s'], tw_rad_wig_off ['bety'])

spco.plot(tw_rad_wig_off ['s'], tw_rad_wig_off ['x'])
spco.plot(tw_rad_wig_off ['s'], tw_rad_wig_off ['y'])

spdisp.plot(tw_rad_wig_off ['s'], tw_rad_wig_off ['dx'])
# spdisp.plot(tw_rad_wig_off ['s'], tw_rad_wig_off ['dy'])

spbet.set_xlim(tw_rad_wig_off ['s', 'ip.4'] - 1000, tw_rad_wig_off ['s', 'ip.4'] + 500)

spbet.set_ylabel(r'$\beta_{x,y}$ [m]')
spco.set_ylabel(r'(Closed orbit)$_{x,y}$ [m]')
spdisp.set_ylabel(r'$D_{x,y}$ [m]')
spdisp.set_xlabel('s [m]')

fig1.suptitle(
    r'$q_x$ = ' f'{tw_rad_wig_off ["qx"]:.5f}' r' $q_y$ = ' f'{tw_rad_wig_off ["qy"]:.5f}' '\n'
    r"$Q'_x$ = " f'{tw_rad_wig_off ["dqx"]:.2f}' r" $Q'_y$ = " f'{tw_rad_wig_off ["dqy"]:.2f}'
    r' $\gamma_{tr}$ = '  f'{1/np.sqrt(tw_rad_wig_off ["momentum_compaction_factor"]):.2f}'
)

fig1.subplots_adjust(left=.15, right=.92, hspace=.27)
plt.savefig('twiss_rad_wig_off.png')