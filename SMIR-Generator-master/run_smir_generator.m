%% Initialization
%close all
%clear
%clc

% Setup
procFs = 48000;                      % Sampling frequency (Hz)
c = 343;                            % Sound velocity (m/s)
nsample = 4096;                   % Length of desired RIR
N_harm = 36;                        % Maximum order of harmonics to use in SHD
K = 1;                              % Oversampling factor

L = [6 6 3];                        % Room dimensions (x,y,z) in m
sphLocation = [3 3 1.5];              % Receiver location (x,y,z) in m
s = [5 3 1.5];                        % Source location(s) (x,y,z) in m

HP = 1;                             % Optional high pass filter (0/1)
src_type = 'o';                     % Directional source type ('o','c','s','h','b')
[src_ang(1),src_ang(2)] = mycart2sph(sphLocation(1)-s(1),sphLocation(2)-s(2),sphLocation(3)-s(3)); % Towards the receiver

% Example 1
order = 10;                          % Reflection order (-1 is maximum reflection order)
refl_coeff_ang_dep = 0;             % Real reflection coeff(0) or angle dependent reflection coeff(1)
% beta = 0.3;                         % Reverbration time T_60 (s)
beta = [1 0.7 0.7 0.5 0.2 1];             % Room reflection coefficients [\beta_x_1 \beta_x_2 \beta_y_1 \beta_y_2 \beta_z_1 \beta_z_2]

sphRadius = 0.042;                  % Radius of the spherical microphone array (m)
sphType = 'rigid';                  % Type of sphere (open/rigid)
mic = [0 0; pi/2 0; pi 0; 3*pi/2 0];                  % Microphone positions (azimuth, elevation)
%mic = [0 pi/4; pi/2 3*pi/4; pi pi/4; 3*pi/2 3*pi/4];                  % Microphone positions (azimuth, elevation)

[h1, H1] = smir_generator(c, procFs, sphLocation, s, L, beta, sphType, sphRadius, mic, N_harm, nsample, K, order, refl_coeff_ang_dep, HP, src_type, src_ang);

%% Example 2
% order = 6;                          % Reflection order (-1 is maximum reflection order)
% refl_coeff_ang_dep = 1;             % Real reflection coeff(0) or angle dependent reflection coeff(1)
% sigma = 1.5*10^4*ones(1,6);         % "Effective" flow resistivity; typical values between 10^3 and 10^9
% 
% sphRadius = 0.042;                  % Radius of the spherical microphone array (m)
% sphType = 'rigid';                  % Type of sphere (open/rigid)
% mic = [pi/4 pi; pi/2 pi];		    % Microphone positions (azimuth, elevation)
% 
% [h2, H2] = smir_generator(c, procFs, sphLocation, s, L, sigma, sphType, sphRadius, mic, N_harm, nsample, K, order, refl_coeff_ang_dep, HP, src_type, src_ang);

%% Example 3 (single microphone)

% order = 6;                          % Reflection order (-1 is maximum reflection order)
% refl_coeff_ang_dep = 0;             % Real reflection coeff(0) or angle dependent reflection coeff(1)
% beta = 0.3;                         % Reverbration time T_60 (s)
% % beta = 0.2*ones(1,6);             % Room reflection coefficients [\beta_x_1 \beta_x_2 \beta_y_1 \beta_y_2 \beta_z_1 \beta_z_2]
% 
% sphRadius = 0;                      % Single microphone at the center of the sphere with radius zero
% sphType = 'open';                   % Type of sphere (open/rigid)
% mic = [0 0];			            % Microphone positions (azimuth, elevation)
% 
% [h3, H3] = smir_generator(c, procFs, sphLocation, s, L, beta, sphType, sphRadius, mic, N_harm, nsample, K, order, refl_coeff_ang_dep, HP, src_type, src_ang);

%% Plotting

mic_to_plot = 1;

figure(1);
ax1(1)=subplot(411);
plot([0:nsample-1]/procFs,h1(mic_to_plot,1:nsample), 'r')
xlim([0 (nsample-1)/procFs]);
title(['Room impulse response at microphone ', num2str(mic_to_plot),' (real refl coeff)']);
xlabel('Time (s)');
ylabel('Amplitude');

mic_to_plot = 2;

figure(1);
ax1(1)=subplot(412);
plot([0:nsample-1]/procFs,h1(mic_to_plot,1:nsample), 'r')
xlim([0 (nsample-1)/procFs]);
title(['Room impulse response at microphone ', num2str(mic_to_plot),' (real refl coeff)']);
xlabel('Time (s)');
ylabel('Amplitude');

mic_to_plot = 3;

figure(1);
ax1(1)=subplot(413);
plot([0:nsample-1]/procFs,h1(mic_to_plot,1:nsample), 'r')
xlim([0 (nsample-1)/procFs]);
title(['Room impulse response at microphone ', num2str(mic_to_plot),' (real refl coeff)']);
xlabel('Time (s)');
ylabel('Amplitude');

mic_to_plot = 4;

figure(1);
ax1(1)=subplot(414);
plot([0:nsample-1]/procFs,h1(mic_to_plot,1:nsample), 'r')
xlim([0 (nsample-1)/procFs]);
title(['Room impulse response at microphone ', num2str(mic_to_plot),' (real refl coeff)']);
xlabel('Time (s)');
ylabel('Amplitude');


%% Ambisonics

W = h1(1,1:nsample) + h1(2,1:nsample) + h1(3,1:nsample) + h1(4,1:nsample);
X = cos(mic(1,1))*sin(mic(1,2))*h1(1,1:nsample) + cos(mic(2,1))*sin(mic(2,2))*h1(2,1:nsample) + cos(mic(3,1))*sin(mic(3,2))*h1(3,1:nsample) + cos(mic(4,1))*sin(mic(4,2))*h1(4,1:nsample);
Y = sin(mic(1,1))*sin(mic(1,2))*h1(1,1:nsample) + sin(mic(2,1))*sin(mic(2,2))*h1(2,1:nsample) + sin(mic(3,1))*sin(mic(3,2))*h1(3,1:nsample) + sin(mic(4,1))*sin(mic(4,2))*h1(4,1:nsample);
Z = cos(mic(1,2))*h1(1,1:nsample) + cos(mic(2,2))*h1(2,1:nsample) + cos(mic(3,2))*h1(3,1:nsample) + cos(mic(4,2))*h1(4,1:nsample);

figure(2);
ax1(1)=subplot(411);
plot([0:nsample-1]/procFs,W, 'r')
xlim([0 (nsample-1)/procFs]);

ax1(1)=subplot(412);
plot([0:nsample-1]/procFs,X, 'r')
xlim([0 (nsample-1)/procFs]);

ax1(1)=subplot(413);
plot([0:nsample-1]/procFs,Y, 'r')
xlim([0 (nsample-1)/procFs]);

ax1(1)=subplot(414);
plot([0:nsample-1]/procFs,Z, 'r')
xlim([0 (nsample-1)/procFs]);

% ax1(2)=subplot(212);
% plot([0:nsample-1]/procFs,h2(mic_to_plot,1:nsample), 'r')
% xlim([0 (nsample-1)/procFs]);
% title(['Room impulse response at microphone ', num2str(mic_to_plot), ' (angle dependent refl coeff)']);        % open sphere
% xlabel('Time (s)');
% ylabel('Amplitude');
% linkaxes(ax1);