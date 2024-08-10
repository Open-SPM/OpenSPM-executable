load('G_freqresp - id_contact');
G1=G_freqresp;
load('G_freqresp - id_ort_200Hz');
G2=G_freqresp;
load('G_freqresp - id_ort_500Hz');
G3=G_freqresp;
load('G_freqresp - id_ort_noHP');
G4=G_freqresp;
bodemag(G1,G2,G3,G4);
legend;


