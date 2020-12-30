import WavLib as wl
import numpy as np
from matplotlib import pyplot as plt
import time

#Methode um Rauschen auf Funktion zu legen, gibt Verrauschte Funktion wieder
def noisefct(fct,sigma=1,mu=0):
    N=len(fct)
    return fct+(sigma*np.random.randn(N)+mu)

#definiert sigmoid zu testzwecken
def sigmoid(x):
    return 1/(1+np.exp(-x))

#Truncation Operator:
#schneidet alles ab was kleiner m ist
def trunc(f,m):
    Tf=np.zeros(len(f))
    for i,v in enumerate(f):
        if abs(v)>=m:
            Tf[i]=v
    return Tf

#berechnet standartabweichung:
def standabw(data,func):
    N=len(data)
    return np.sqrt(1/N*sum((data-func)**2))

#wird benutzt für Entropie H
def p(fk,f):
    return (abs(fk)/np.linalg.norm(f))**2

#Quadrat der Norm
def Norm(f):
    return sum(f**2)

#Entropie:
def H(data):
    H=0
    for k in data:
        if p(k, data)!=0:
            H=H+p(k, data)*np.log(1/p(k, data))
    return H

#Analyse Algorithmus: gibt Coherenten Teil zur Funktion und Rest wieder
def AnAlg(data,traf=wl.Haar,cost=wl.ml2logl2):
    Rest=data
    coh=np.zeros(np.shape(data))
    #Referenz Entropie
    Href=H(data)
    #Referenz Norm
    Normref=Norm(nfct-fct) #hier könnte Verteilungsfct genutzt werden
    n=0
    #Entropie=H(wl.giveBestBasis(Rest,traf,cost)[0])
    norm=Norm(Rest)
    Start=time.time()
    while norm>Normref:
        #Bilde BestBasis:
        BB,pos=wl.giveBestBasis(Rest,traf,cost)

        #benutze als Truncation-Parameter größten Wert der BestBasis:
        m=np.amax(np.abs(BB))
        #m=BB[int(np.exp(H(BB)))]
        
        #bilde Rücktrafo von Truncation-Operator(BestBasis):
        rücktraf=wl.iWavTraf( (trunc(BB,m),pos) )

        #aktualisiere Coherenten Teil und Rest
        coh+=rücktraf
        Rest-=rücktraf

        #Entropie=H(wl.giveBestBasis(Rest,traf,cost)[0])
        n+=1
        norm=Norm(Rest)
        #print(str(n) + ': Entropie: ' + str(norm) )
    End=time.time()
    print('Steps:', n)
    print('Processtime:', End-Start,'s')


    return (coh,Rest)

def printdata():
    global x, fct, rand, Coherent, Rest

    print('Standartabweichung Rauschen zu f: ' + str(standabw(fct+rand,fct)))
    print('Standartabweichung Coherenter Teil zu f: ' + str(standabw(Coherent,fct)))
    print('Rauschen wurde um ' + str(standabw(fct+rand,fct)-standabw(Coherent,fct)) + ' reduziert')
    print('1-sCoh/sRausch = ' + str((1-standabw(Coherent,fct)/standabw(fct+rand,fct))*100) + '%')

def plotdata():
    global x, fct, rand, Coherent, Rest

    fig=plt.figure()

    ax1 = fig.add_subplot(1,2,1)
    ax1.plot(x,fct, x,fct+rand, x,rand)
    ax1.legend(['Function','Noisefunction','rand'])

    ax2 = fig.add_subplot(1,2,2)
    ax2.plot(x,fct, x,Coherent, x,Rest)
    ax2.legend(['Function','Coherent','Rest'])

    plt.show()

#create Data:
n=2**7
N=2**int(np.around(np.log2(n)))
x=np.linspace(0,2*np.pi,N)
fct = -np.sin(x) + np.cos(x)
#fct = np.sin(x) + np.sin(3*x) + np.sin(5*x)
#x=np.linspace(-6,6,N)
#fct = sigmoid(x)+1
rand = np.random.normal(0,0.09,len(x))

nfct=fct + rand
print('Algorithmus ohne Pywavelet-Lybrary:')
Coherent,Rest=AnAlg(nfct)

printdata()
plotdata()

##############################################################################

#Do the same with pwt:
nfct=fct+rand
print('')
print('Algorithmus mit Pywavelet-Lybrary:')
Coherent,Rest=wl.pwtAnAlg(nfct, Norm(nfct-fct))

printdata()
plotdata()

##############################################################################

print('')
print('Variation der Kostenfunktion (ml2logl2 zu l2Norm):')

nfct=fct+rand
Coherent,Rest=wl.pwtAnAlg(nfct, Norm(nfct-fct), cost=wl.lpnorm,)

printdata()

##############################################################################

print('')
print('Variation von m (den 5. größten Wert, Kostenfunktion wieder auf ml2logl2):')

nfct=fct+rand
Coherent,Rest=wl.pwtAnAlg(nfct, Norm(nfct-fct), d=5)

printdata()
print()

###############################################################################

input('zum fortfahren bitte beliebige Taste drücken...')
print()
print('Untersuchung über Fourier-Moden:')
print()
print('f=sin(x)+sin(3x)+sin(4x)')

fct = np.sin(x)+np.sin(3*x)+np.sin(4*x)
nfct=fct+rand
Coherent,Rest=wl.pwtAnAlg(nfct, Norm(nfct-fct))

printdata()
plotdata()

###############################################################################

print()
print('f=sin(x)+sin(3x)+sin(4x)+sin(9*x)')

fct = np.sin(x)+np.sin(3*x)+np.sin(4*x)+np.sin(9*x)
nfct=fct+rand
Coherent,Rest=wl.pwtAnAlg(nfct, Norm(nfct-fct))

printdata()
plotdata()

###############################################################################
print()
input('zum fortfahren bitte beliebige Taste drücken...')
print()
print('Im folgenden wird das Rauschen erhöht (von 0.09 zu 0.2):')
print()
print('f=sin(x)+sin(3x)+sin(4x)')

fct = np.sin(x)+np.sin(3*x)+np.sin(4*x)
rand = np.random.normal(0,0.2,len(x))
nfct=fct+rand
Coherent,Rest=wl.pwtAnAlg(nfct, Norm(nfct-fct))

printdata()

###############################################################################

print()
print('Im folgenden wird das Rauschen erhöht (von 0.09 zu 0.3):')
print()
print('f=sin(x)+sin(3x)+sin(4x)')

rand = np.random.normal(0,0.3,len(x))
nfct=fct+rand
Coherent,Rest=wl.pwtAnAlg(nfct, Norm(nfct-fct))

printdata()

###############################################################################

print()
print('Im folgenden wird das Rauschen erhöht (von 0.09 zu 0.9):')
print()
print('f=sin(x)+sin(3x)+sin(4x)')

rand = np.random.normal(0,0.9,len(x))
nfct=fct+rand
Coherent,Rest=wl.pwtAnAlg(nfct, Norm(nfct-fct))

printdata()

fig=plt.figure()

ax1 = fig.add_subplot(1,2,1)
ax1.plot(x,fct, x,fct+rand)
ax1.legend(['Function','rand'])

ax2 = fig.add_subplot(1,2,2)
ax2.plot(x,fct, x,Coherent)
ax2.legend(['Function','Coherent'])

plt.show()