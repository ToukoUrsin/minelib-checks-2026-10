param NBLOCKS;
param NPERIODS;
param NDESTINATIONS;
param NRESOURCE_SIDE_CONSTRAINTS;
param DISCOUNT_RATE;
set setBL = 0..NBLOCKS-1;
set setT = 0..NPERIODS-1;
set setSIDE = 0..NRESOURCE_SIDE_CONSTRAINTS-1;
set setDEST = 0..NDESTINATIONS-1;

param RESOURCE_CONSTRAINT_UB_LIMITS {setSIDE,setT};
param RESOURCE_CONSTRAINT_LB_LIMITS {setSIDE,setT};
param RESOURCE_CONSTRAINT_COEFFICIENTS {setBL, setSIDE, setDEST} default 0;
param OBJECTIVE_FUNCTION {setBL,setDEST};
set PREC{setBL};

var X{setBL,setT} binary;
var Y{setBL,setDEST,setT} >=0, <=1;

maximize Profit: sum{t in setT} sum {d in setDEST} sum{b in setBL} (1.0/(1.0 + DISCOUNT_RATE))^t * OBJECTIVE_FUNCTION[b,d] * Y[b,d,t];

subject to Resource { r in setSIDE, t in setT}:
		RESOURCE_CONSTRAINT_LB_LIMITS[r,t] <= sum{b in setBL} sum {d in setDEST} RESOURCE_CONSTRAINT_COEFFICIENTS[b,r,d] * Y[b,d,t] <= RESOURCE_CONSTRAINT_UB_LIMITS[r,t];

subject to CliqueBlock {b in setBL}:
		sum{t in setT} X[b,t] <= 1;

subject to SumDest {b in setBL, t in setT}:
		sum {d in setDEST} Y[b,d,t] = X[b,t];

subject to Precedence {b in setBL, i in PREC[b], t in setT}:
    sum{s in 0..t} X[b,s] <= sum{s in 0..t} X[i,s];



		
