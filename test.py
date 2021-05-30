import opensimplex


simp = opensimplex.OpenSimplex(seed=1)

SMOOTHNESS = 10
DEPTH = .2

map = [[ int(simp.noise2d(x=x*SMOOTHNESS, y=y*SMOOTHNESS) > DEPTH) for x in range(10)] for y in range(10)] 

map = [[simp.noise2d(x=x*SMOOTHNESS, y=y*SMOOTHNESS) for x in range(10)] for y in range(10)] 
for i in map:
    print(i)