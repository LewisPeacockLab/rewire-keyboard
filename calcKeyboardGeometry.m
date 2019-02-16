%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% find distance from spring to pivot %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% L1 = 35; % distance from spring to finger (mm)
% d1 = 4; % desired max finger press deflection (mm)
% Ff = 2; % desired max force at max deflection (N)
% k = 1.138; % spring constant (N/mm)

offset_back = 5;
offset_fwd = 5;

L1 = 35+offset_back; % distance from spring to finger (mm)
d1 = 4; % desired max finger press deflection (mm)
Ff = 1.5; % desired max force at max deflection (N)
k = 1.279; % spring constant (N/mm) (0.375in)
% k = 1.138; % spring constant (N/mm) (0.5in)

syms L2 d2; % distance from spring to pivot (mm) and deflection of spring (mm)
eqn1 = Ff*(L1+L2)-k*(d1*L2-d2*L1)==0; % equal force equation
eqn2 = d2*(L1+L2)-d1*L2==0; % equal torque equation
Y = solve([eqn1,eqn2]);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% find distance from spring to finger %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

old_L1 = L1;
new_L2 = eval(Y.L2(2));

L2 = new_L2+offset_back+offset_fwd; % distance from spring to pivot (mm)
d1 = 4; % desired max finger press deflection (mm)
Ff = 1.5; % desired max force at max deflection (N)
k = 1.279; % spring constant (N/mm) (0.375in)
% k = 1.138; % spring constant (N/mm) (0.5in)

syms L1 d2; % distance from spring to finger (mm) and deflection of spring (mm)
eqn1 = Ff*(L1+L2)-k*(d1*L2-d2*L1)==0; % equal force equation
eqn2 = d2*(L1+L2)-d1*L2==0; % equal torque equation
Y = solve([eqn1,eqn2]);

new_L1 = eval(Y.L1(2)); 

total_dist_short = old_L1+new_L2;
total_dist_long = L2+new_L1;
finger_offset = total_dist_long-total_dist_short;

target_deadweight = 0.4; % spring force at zero deflection

short_preload = total_dist_short*target_deadweight/new_L2
long_preload = total_dist_long*target_deadweight/L2
