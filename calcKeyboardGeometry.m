%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% find distance from spring to pivot %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% L1 = 35; % distance from spring to finger (mm)
% d1 = 4; % desired max finger press deflection (mm)
% Ff = 2; % desired max force at max deflection (N)
% k = 1.138; % spring constant (N/mm)

L1 = 35; % distance from spring to finger (mm)
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

L2 = 60.55; % distance from spring to pivot (mm)
d1 = 4; % desired max finger press deflection (mm)
Ff = 2; % desired max force at max deflection (N)
k = 1.138; % spring constant (N/mm)

syms L1 d2; % distance from spring to finger (mm) and deflection of spring (mm)
eqn1 = Ff*(L1+L2)-k*(d1*L2-d2*L1)==0; % equal force equation
eqn2 = d2*(L1+L2)-d1*L2==0; % equal torque equation
Y = solve([eqn1,eqn2]);
