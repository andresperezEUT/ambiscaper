% (C) Andres Perez Lopez, 2018


%%% Script to be called from AmbiScaper (python)
%%% All values (should) have been already loaded from matlab_engine.put('x',x)...

[h, H] = smir_generator(c, procFs, sphLocation, s, L, beta, sphType, sphRadius, mic, N_harm, nsample, K, order, refl_coeff_ang_dep, HP, src_type);

