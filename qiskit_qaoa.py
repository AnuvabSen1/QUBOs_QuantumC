# -*- coding: utf-8 -*-
"""Qiskit QAOA.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JuMMG6sR7gZRsZ6lL33j-MRnNckI1J0_

#Solving QUBOs with Qiskit-Optimization QAOA

Date: December 4th, 2023

The notebook contains materials supporting the tutorial paper:
*Five Starter Problems: Solving QUBOs on Quantum Computers* by Arul Rhik Mazumder (arulm@andrew.cmu.edu) and Sridhar Tayur (stayur@cmu.edu).
It depends on various packages shown below.

### **Introduction**

Qiskit-Optimization is a part of IBM Qiskit's open source quantum computing framework. It provides easy high-level applications of quantum algorithms that can run on both classical and quantum simulators. It provides a wide array of algorithms and built-in application classes for NP-Hard problems. For this paper, we only focus on QAOA and ignore the built-in application classes to take advantage of the its docplex modelling capabilities. By defining custom QUBOs instead of relying on predefined classes, users can more easily implement and solve their own QUBO models using qiskit-opimization.

Qiskit-Optimization is an extremely useful and easy way to solve QUBOs with various quantum algorithms including Variational Quantum Eigensolver, Adaptive Grovers and the earlier mentioned QAOA. Furthermore because of compatibility with IBMQ, algorithms can run on actual IBM quantum backends. In the examples below, all code is run by default on the Qiskit QASM simulator. Although base level implementation is easier, customization and indepth analysis in more difficult. Tasks like plotting optimization history or bitstring distributions, although possible, are significantly more challenging. Qiskit-Optimization's key limitations are its extremely long optimization times and limited set of optimizers.  It is very slow in solving QUBOs with over 10 variables and was measured to take almost 45 minutes for a QUBO with only 18 variables however accurate. Furthermore there is a defined set optimizers shown below:

https://qiskit.org/documentation/stubs/qiskit.algorithms.optimizers.html

Although there is an a pretty expansive set of local and global optimizers it is difficult to use any optimizer not. Thus it is impossible to implement many promising algorithms like Adagrad and Genetic Algorithm as classical optimizers.

Using Qiskit Runtime further customization such as error mitigation, custom ansatz circuits, and custom cost hamiltonians are possible, but require more advanced knowledge. More information is provided in the link below:

https://qiskit.org/ecosystem/optimization/tutorials/12_qaoa_runtime.html
"""

try:
  import google.colab
  IN_COLAB = True
except:
  IN_COLAB = False

if IN_COLAB:
 !pip install -q qiskit==0.39.2
 !pip install -q qiskit-optimization==0.5.0
 print("All Packages Installed!")

# Problem Modelling Imports
from qiskit_optimization.converters.quadratic_program_to_qubo import QuadraticProgramToQubo
from qiskit_optimization.translators import from_docplex_mp
from docplex.mp.model import Model

# Qiskit Optimizer Imports
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.algorithms.minimum_eigensolvers import QAOA
from qiskit.algorithms.optimizers import SPSA, COBYLA, NELDER_MEAD

from qiskit.primitives import Sampler

# Misc. Imports
import time
import matplotlib.pyplot as plt

"""### **Example 1 - Number Partitioning Problem**"""

test_1 = [1, 7, 10, 18]
test_2 = [11, 29, 21, 17, 32, 10]
test_3 = [25, 7, 13, 31, 42, 17, 21, 10]

arr = test_2
n = len(arr)
c = sum(arr)

"""**Number Partitioning Models**

Given an array of $n$ integers $[a_{1}, a_{2}, a_{3} ... a_{n}]$, the corresponding Ising Hamiltonian is:

$$H=(\sum_{i=1}^{n}a_{i}s_{i})^2$$

Where $s_{i} \in \{-1,1\}$ is the Ising spin variable.

Similarly the corresponding QUBO Model is:

$$Q=(\sum_{i=1}^{n}a_{i}-2\sum_{i=1}^{n}a_{i}x_{i})^{2}$$
or
$$Q=(c-2\sum_{i=1}^{n}a_{i}x_{i})^{2}$$

Where $c=\sum_{i=1}^{n}a_{i}$ and $x_{i} \in \{0, 1\}$ is a binary quadratic variable.
"""

model = Model()
x = model.binary_var_list(n)
Q = (c - 2*sum(arr[i]*x[i] for i in range(n)))**2
model.minimize(Q)
problem = from_docplex_mp(model)
qubo = QuadraticProgramToQubo().convert(problem)

"""**Solving the QUBO**

This algorithm uses the Simultaneous Perturbation Stochastic Approximation (SPSA) optimizers. It is one of the gradient-free optimization algorithms offered by Qiskit-Optimization and is well suited uncertain or noisy objective functions. In this SPSA is run for a maximum of 250 iterations

The sampler reference the base sampler used by Qiskit. This sampler finds the probability of bitstring solutions. Finally the QAOA uses the optimizer and sampler to create the quantum circuit to run on the QASM Simulator. You can further specify the number of reps which describes the number of iterations of cost and mixer hamiltonians. In this example and all following circuits, this has been set to $p=2$.

The Minimum Eigen Optimizer converts the QUBO problems to Ising Model and then solves it using the quantum circuit defined before.

"""

spsa = SPSA(maxiter=250)
sampler = Sampler()
qaoa = QAOA(sampler=sampler, optimizer=spsa, reps=2)
algorithm = MinimumEigenOptimizer(qaoa)

result = algorithm.solve(problem)
#print(result.prettyprint())
elapsed_time = result.min_eigen_solver_result.optimizer_time

# Converting the output binary variables to produce a valid output
def partition(binary_dict):
    P1 = []
    P2 = []
    for key, value in binary_dict.items():
        if value == 0:
            P1.append(arr[int(key[1:])])
        elif value == 1:
            P2.append(arr[int(key[1:])])
    sum1 = sum(P1)
    sum2 = sum(P2)
    if print is not None:
      print(P1)
      print('Sum: ' + str(sum1))
      print(P2)
      print('Sum: ' + str(sum2))
    return abs(sum1 - sum2)

partition(result.variables_dict)
print("Optimization Time: " + str(elapsed_time))

"""### **Example 2 - Max-Cut Problem**"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def draw_graph(G, colors, pos):
    default_axes = plt.axes()
    nx.draw_networkx(G, node_color=colors, node_size=600, alpha=0.8, ax=default_axes, pos=pos)
    edge_labels = nx.get_edge_attributes(G, "weight")

# Generating a graph of 4 nodes

n = 5  # Number of nodes in graph
G = nx.Graph()
G.add_nodes_from(np.arange(0, n, 1))
edges = [(0, 1, 1.0), (0, 3, 1.0), (1, 2, 1.0), (2, 3, 1.0), (2, 4, 1.0), (3, 4, 1.0)]
# tuple is (i,j,weight) where (i,j) is the edge
G.add_weighted_edges_from(edges)

colors = ["r" for node in G.nodes()]
pos = nx.spring_layout(G)

draw_graph(G, colors, pos)

"""**Max-Cut Models**

Given an undirected unweighted Graph $G$ with vertex set $V$ and edge set $E$ with edges $(i, j)$ the corresponding Ising Hamiltonian is:

$$H=\sum_{(i, j) \in E}\frac{1-s_{i}s_{j}}{2}$$

Where $s_{i} \in \{-1,1\}$ is the Ising spin variable.

The corresponding QUBO Model is:

$$Q=\sum_{(i, j)\in E}(x_{i}+x_{j}-2x_{i}x_{j})$$

Where $x_{i} \in \{0, 1\}$ is a binary quadratic variable.
"""

model = Model()
x = model.binary_var_list(n)
H = sum(2*x[e[0]]*x[e[1]] - x[e[0]] - x[e[1]] for e in edges)
model.minimize(H)
problem = from_docplex_mp(model)
qubo = QuadraticProgramToQubo().convert(problem)

"""**Solving the QUBO**

Other than the features shared with Number Partitioning Partition, this algorithm uses the Constrained by Linear Approximation (COBYLA) optimizers. It is another gradient-free optimization algorithms offered by Qiskit-Optimization. It is similarly run for 250 iterations and is one of the most popularly used QAOA optimizers due to its tradeoff of speed and accuracy.
"""

cobyla = COBYLA(maxiter=250)
sampler = Sampler()
qaoa = QAOA(sampler=sampler, optimizer=cobyla, reps=2)
algorithm = MinimumEigenOptimizer(qaoa)

result = algorithm.solve(problem)
print(result.prettyprint())
elapsed_time = result.min_eigen_solver_result.optimizer_time
print("Optimization Time: " + str(elapsed_time))

# Converting the output binary variables to produce a valid output
colors = ["r" if result.variables_dict[v] == 0.0 else "c" for v in result.variables_dict.keys()]
draw_graph(G, colors, pos)
print("Optimization Time: " + str(elapsed_time))

"""### **Example 3 - Minimum Vertex Cover**"""

# Generating a graph of 4 nodes

n = 5  # Number of nodes in graph
G = nx.Graph()
G.add_nodes_from(np.arange(0, n, 1))
edges = [(0, 2, 1.0), (2, 4, 1.0), (1, 4, 1.0), (3, 4, 1.0)]
# tuple is (i,j,weight) where (i,j) is the edge
G.add_weighted_edges_from(edges)

colors = ["r" for node in G.nodes()]
pos = nx.spring_layout(G)

draw_graph(G, colors, pos)

"""**Minimum Vertex Cover Models**

Given an undirected unweighted Graph $G$ with vertex set $V$ with vertices $i$ and edge set $E$ with edges $(i, j)$ the corresponding Ising Hamiltonian is:

$$H=P\sum_{(i, j) \in E}(1-s_{i})(1-s_{j}) + \sum_{i \in V}s_{i}$$

Where $s_{i} \in \{-1,1\}$ is the Ising spin variable and $P$ is the penalty coefficient.

The corresponding QUBO Model is:

$$Q=\sum_{i \in V}x_{i} + P(\sum_{(i, j) \in E}(1-x_{i}-x_{j}+x_{i}x_{j}))$$

Where $x_{i} \in \{0, 1\}$ is a binary quadratic variable.

Note in the example $P$ was chosen through trial-and-error although there exists rigorous mathematical processes
"""

model = Model()
x = model.binary_var_list(n)
P = 10
H = sum(x[i] for i in range(n)) + P*sum(1 - x[e[0]] - x[e[1]] + x[e[0]]*x[e[1]] for e in edges)
model.minimize(H)
problem = from_docplex_mp(model)
qubo = QuadraticProgramToQubo().convert(problem)

"""**Solving the QUBO**

Other than the features shared with Number Partitioning Partition, this algorithm uses the Nelder optimizers. It is another gradient-free optimization algorithms offered by Qiskit-Optimization. It is great for solving nondifferentiable, nonlinear, and noisy functions by iterative evolving a simplex and is similarly run for 250 iterations.
"""

nelder_mead = NELDER_MEAD(maxiter=250)
sampler = Sampler()
qaoa = QAOA(sampler=sampler, optimizer=nelder_mead, reps=2)
algorithm = MinimumEigenOptimizer(qaoa)

result = algorithm.solve(problem)
print(result.prettyprint())
elapsed_time = result.min_eigen_solver_result.optimizer_time
print("Optimization Time: " + str(elapsed_time))

# Converting the output binary variables to produce a valid output
colors = ["r" if result.variables_dict[v] == 0.0 else "c" for v in result.variables_dict.keys()]
draw_graph(G, colors, pos)
print("Execution Time: " + str(elapsed_time))