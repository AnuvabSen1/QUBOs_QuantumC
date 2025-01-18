# -*- coding: utf-8 -*-
"""Notebook 5 - DWAVE Quantum Annealing.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MLvWoaa_B6D2a3-N096_EnKR2QHxKAzm

#Solving QUBOs with DWAVE Quantum Annealing

### **Introduction**

D-Wave Ocean is a software stack and suite of tools provided by D-Wave Systems, a company specializing in quantum computing hardware based on quantum annealing technology. D-Wave Ocean is designed to support the development and execution of quantum annealing applications. Quantum annealing is a specialized approach to quantum computing that focuses on solving optimization problems.

D-Wave provides cloud-based access to their quantum annealing processors through the Leap cloud service. Users can access quantum annealing resources remotely, allowing them to run optimization problems on D-Wave's hardware. Their Ocean software stack includes various software tools and libraries that help users formulate, optimize, and solve problems using quantum annealers. It provides high-level abstractions for working with quantum annealing and includes tools for problem modeling, hybrid solvers, and more. More details regarding DWAVE Ocean functionalities can be found in the link below:

https://docs.ocean.dwavesys.com/en/stable/
"""

try:
  import google.colab
  IN_COLAB = True
except:
  IN_COLAB = False
if IN_COLAB:
  !pip install -q dwave-ocean-sdk==6.10.0
  !pip install -q bravado==11.0.3
  !pip install -q pyqubo==1.4.0
  print("All Packages Installed!")

# imports necessary packages to run on a DWAVE Machine
from pyqubo import Spin, Array, Placeholder, Constraint
import dimod
from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
import neal

# Misc. imports
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import random
import time
import os

# Connecting to DWAVE Account
os.environ['DWAVE_API_TOKEN'] = 'ADD YOUR DWAVE API KEY HERE'

"""### **Example 1 - Number Partitioning Problem**

Initializing an arbitrary number partitioning instance.
"""

test_1 = [1, 5, 11, 5]
test_2 = [25, 7, 13, 31, 42, 17, 21, 10]
arr = test_2
print(arr)
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

x = Array.create('x', n, 'BINARY')
H = (c - 2*sum(arr[i]*x[i] for i in range(n)))**2
model = H.compile()
bqm = model.to_bqm()

"""Embedding and running the problem on the the DWAVE Quantum Annealer. The best solution is the first one with the lowest energy."""

sampler = EmbeddingComposite(DWaveSampler())
sampleset = sampler.sample(bqm, num_reads=1000)
sample = sampleset.first

print(sample)

"""Print sampler solving details."""

print(sampleset.info)
elapsed_time = float(sampleset.info['timing']['qpu_access_time'])/1000000

# Converting the output binary variables to produce a valid output
def NPP_measure(sortedSample):
  P1 = []
  P2 = []
  for i in sortedSample.keys():
    if sortedSample[i] == 0:
        P1.append(arr[int(i[2:len(i)-1])])
    else:
        P2.append(arr[int(i[2:len(i)-1])])
  sum1 = sum(P1[i] for i in range(len(P1)))
  sum2 = sum(P2[i] for i in range(len(P2)))
  print(P1)
  print('Sum: ' + str(sum1))
  print(P2)
  print('Sum: ' + str(sum2))
  return abs(sum2-sum1)

#Sorts samples by numbers to see which quadratic variables are 0 and 1
sampleKeys = list(sample.sample.keys())
def sortbynumber(str):
    return int(str[2:len(str)-1])
sampleKeys.sort(key = sortbynumber)
sortedSample = {i: sample.sample[i] for i in sampleKeys}
#print(sortedSample)
print("QPU Access Time: " + str(elapsed_time))
NPP_measure(sortedSample)

"""### **Example 2 - Max-Cut Problem**"""

def draw_graph(G, colors, pos):
    default_axes = plt.axes()
    nx.draw_networkx(G, node_color=colors, node_size=600, alpha=0.8, ax=default_axes, pos=pos)
    edge_labels = nx.get_edge_attributes(G, "weight")

"""Initializing an arbitrary Max-Cut instance."""

# Generating a graph of 4 nodes

n = 5 # Number of nodes in graph
G = nx.Graph()
G.add_nodes_from(np.arange(0, n, 1))
edges = [(0, 1, 1.0), (0, 3, 1.0), (1, 2, 1.0), (2, 3, 1.0), (2, 4, 1.0), (3, 4, 1.0)]
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

x = Array.create('x', n, 'BINARY')
H = sum(2*x[e[0]]*x[e[1]] - x[e[0]] - x[e[1]] for e in edges)
model = H.compile()
bqm = model.to_bqm()

"""Embedding and running the problem on the the DWAVE Quantum Annealer."""

sampler = EmbeddingComposite(DWaveSampler())
sampleset = sampler.sample(bqm, num_reads=1000)
sample = sampleset.first

"""Print sampler solving details."""

print(sampleset.info)
elapsed_time = float(sampleset.info['timing']['qpu_access_time'])/1000000

#Sorts samples by numbers to see which quadratic variables are 0 and 1
sampleKeys = list(sample.sample.keys())
sampleKeys.sort(key = sortbynumber)
sortedSample = {i: sample.sample[i] for i in sampleKeys}
print(sortedSample)

# Converting the output binary variables to produce a valid output
def MaxCut(sortedSample):
  maxcut_sol = []
  for i in sortedSample.keys():
    if sortedSample[i] == 0:
        maxcut_sol.append(0)
    else:
        maxcut_sol.append(1)
  colors = ["r" if maxcut_sol[i] == 0 else "c" for i in range(len(maxcut_sol))]
  draw_graph(G, colors, pos)
  cutsize = 0
  for u, v in G.edges():
    if maxcut_sol[u] != maxcut_sol[v]:
      cutsize += 1
  return cutsize

print("QPU Access Time: " + str(elapsed_time))
print(MaxCut(sortedSample))

"""### **Example 3 - Minimum Vertex Cover**

Initializing an arbitrary Minimum Vertex Cover instance.
"""

# Generating a graph of 4 nodes

n = 6  # Number of nodes in graph
G = nx.Graph()
G.add_nodes_from(np.arange(0, n, 1))
edges = [(0, 1, 1.0), (0, 2, 1.0), (1, 2, 1.0), (1, 3, 1.0), (1, 4, 1.0), (1, 5, 1.0)]
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

x = Array.create('x', n, 'BINARY')
P = 0.5
H = sum(x[i] for i in range(n)) + P*sum(1 - x[e[0]] - x[e[1]] + x[e[0]]*x[e[1]] for e in edges)
model = H.compile()
bqm = model.to_bqm()

"""Embedding and solving the problem on a DWAVE Quantum Annealer."""

sampler = EmbeddingComposite(DWaveSampler())
sampleset = sampler.sample(bqm, num_reads=1000)
sample = sampleset.first

"""Print sampler solving details."""

print(sampleset.info)
elapsed_time = float(sampleset.info['timing']['qpu_access_time'])/1000000

#Sorts samples by numbers to see which quadratic variables are 0 and 1
sampleKeys = list(sample.sample.keys())
sampleKeys.sort(key = sortbynumber)
sortedSample = {i: sample.sample[i] for i in sampleKeys}
print(sortedSample)

# Converting the output binary variables to produce a valid output
def MVC(sortedSample):
  mvc_sol = []
  for i in sortedSample.keys():
    if sortedSample[i] == 0:
        mvc_sol.append(0)
    else:
        mvc_sol.append(1)
  colors = ["r" if mvc_sol[i] == 0 else "c" for i in range(len(mvc_sol))]
  draw_graph(G, colors, pos)
  covered = 0
  for u, v in G.edges():
    if mvc_sol[u] == 1 or mvc_sol[v] == 1:
      covered += 1
  return covered

print("QPU Access Time: " + str(elapsed_time))
print(MVC(sortedSample))

"""### **Example 4 - Cancer Genomics**

Identifying Cancer Gene Pathways from the TCGA-AML Data. The techniques used were taken from: https://www.biorxiv.org/content/10.1101/845719v1
"""

# import necessary package for data imports
from bravado.client import SwaggerClient
from itertools import combinations

# connects to cbioportal to access data
cbioportal = SwaggerClient.from_url('https://www.cbioportal.org/api/v2/api-docs',
                                    config={"validate_requests":False,"validate_responses":False,"validate_swagger_spec":False})

"""Accessing AML study data from the cbioportal."""

# accesses cbioportal's AML study data
aml = cbioportal.Cancer_Types.getCancerTypeUsingGET(cancerTypeId='aml').result()

# access the patient data of AML study
patients = cbioportal.Patients.getAllPatientsInStudyUsingGET(studyId='laml_tcga').result()

# for each mutation, creates a list of properties associated with the mutation include geneID, patientID, and more
InitialMutations = cbioportal.Mutations.getMutationsInMolecularProfileBySampleListIdUsingGET(
    molecularProfileId='laml_tcga_mutations',
    sampleListId='laml_tcga_all',
    projection='DETAILED'
).result()

"""Identifying the $33$ most common genes from the study.

Then preprocessing the data to create a Patient-Gene Dictionary to construct the matrices from.
"""

# tests if data is correct
# Compares the frequency of the 33 most common genes and compares them with the information listed on
# https://www.cbioportal.org/study/summary?id=laml_tcga
from collections import Counter
mutation_counts = Counter([m.gene.hugoGeneSymbol for m in InitialMutations])
MostImportantMutationsCounts = mutation_counts.most_common(33)
MostImportantMutations = []
for i in range(len(MostImportantMutationsCounts)):
    MostImportantMutations.append(MostImportantMutationsCounts[i][0])

# Sort the patients by index
def sortPatients(m):
    return m.patientId

mutations = []
for m in InitialMutations:
    if m.gene.hugoGeneSymbol in MostImportantMutations:
        mutations.append(m)
geneset = set()

for m in mutations:
    geneset.add(m.gene.hugoGeneSymbol)
# creates a patient-(gene-list) dictionary

PatientGeneDict = {}
mutations.sort(key = sortPatients)

for m in mutations:
    if m.patientId in PatientGeneDict.keys(): # if the patient is already in dictionary add the gene to their previous gene list
        PatientGeneDict[m.patientId].append(m.gene.hugoGeneSymbol)
    else:
        PatientGeneDict[m.patientId] = [m.gene.hugoGeneSymbol] # else add the patient their associated gene

# create independent patient and gene lists
patientset = set()
for m in mutations:
    patientset.add(m.patientId)
patientList = [] # patient list
for m in patientset:
    patientList.append(m)
geneList = [] # gene list
for gene in geneset:
    geneList.append(gene)
geneList.sort()

for key in PatientGeneDict:
    PatientGeneDict[key] = list(set(PatientGeneDict[key]))

"""Patient-Gene Dictionary that displays each patient and their corresponding gene-list."""

# Organized way to visualize the patient-(gene-list) dictionary
print("Patient-Gene Dictionary:")
for k in PatientGeneDict.keys():
    print(k)
    print(PatientGeneDict[k])

"""Create the diagonal $\mathbf{D}$ matrix to represent gene-coverage."""

import numpy as np
D = np.zeros((n, n))
for i in range(n):
    count = 0
    for k in PatientGeneDict.keys():
        if geneList[i] in PatientGeneDict[k]:
            count += 1
        D[i][i] = count

"""Generate gene pairs to create the $\mathbf{A}$ exclusivity matrix"""

def generate_pairs(lst):
    pairs = set()
    for subset in combinations(lst, 2):
        pairs.add(tuple(sorted(subset)))
    return pairs

"""Using the patient-gene dictionary, we identify all gene-pairs for each patient. This used to create the $\mathbf{A}$ matrix."""

# creates a patient-(gene-list-pair) dictionary
PatientGeneDictPairs = {}
for m in mutations:
        PatientGeneDictPairs[m.patientId] = generate_pairs(PatientGeneDict[m.patientId])

"""With all the preprocessing done, the $\mathbf{A}$ matrix is completed.

"""

# creates the A exclusivity matrix
A = np.zeros((n, n))
for j in range(n):
    if i != j:
        count = 0
        for k in PatientGeneDict.keys():
            if (geneList[i], geneList[j]) in PatientGeneDictPairs[k]:
                count += 1
        A[i][j] = count
        A[j][i] = count

"""Identify properties from the gene pathway:"""

# returns the coverage of a gene
def gene_coverage(gene):
    return D[geneList.index(gene)][geneList.index(gene)]

# returns the coverage of a pathway
def coverage(pathway):
    coverage_val = 0
    for i in pathway:
        coverage_val += gene_coverage(i)
    return coverage_val

# returns the indepence(exclusivity) of a pathway
def indep(pathway):
    num_overlap = 0
    for i in pathway:
        for j in pathway:
            if i == j:
                pass
            else:
                num_overlap += A[geneList.index(i)][geneList.index(j)]
    return num_overlap

"""Using the $\mathbf{A}$ and $\mathbf{D}$ matrices, we create the QUBO to identify the Cancer Genes. As stated in "Quantum and Quantum-inspired Methods for de novo
Discovery of Altered Cancer Pathways", the QUBO formulation to identify the cancer gene set while balancing Indepence and Coverage is:

$$\mathbf{Q}=\mathbf{x}^{T}(\mathbf{A}-\alpha \mathbf{D})\mathbf{x}$$

Where $\mathbf{D}$ and $\mathbf{A}$ are the previously found matrices and $\mathbf{x}$ is the vector of binary variables $x_{i}$
"""

# initializes an array of QUBO variables
x = Array.create('x', n, 'BINARY')
H1 = sum(sum(A[i][j]*x[i]*x[j] for j in range(n)) for i in range(n))
H2 = sum(D[i][i]*x[i] for i in range(n))
a = Placeholder("alpha")
H = H1 - a*H2

# creates a Hamiltonian to run on DWAVE sampler
model = H.compile()
feed_dict = {'alpha': 0.45}
bqm = model.to_bqm(feed_dict=feed_dict)

# Getting Results from Sampler
sampler = EmbeddingComposite(DWaveSampler())
sampleset = sampler.sample(bqm, num_reads=1000)
sample = sampleset.first

"""Print sampler solving details."""

print(sampleset.info)
sampleKeys = list(sample.sample.keys())
def sortbynumber(str):
    return int(str[2:len(str)-1])
sampleKeys.sort(key = sortbynumber)
sortedSample = {i: sample.sample[i] for i in sampleKeys}

"""Print the identified pathway"""

pathway = []
for i in sampleKeys:
    if sortedSample[i] == 1:
        pathway.append(geneList[int(i[2:len(i)-1])])
print(pathway)
print("coverage: " + str(coverage(pathway)))
print("coverage/gene: " + str(round(coverage(pathway)/len(pathway), 2)))
print("indep: " + str(indep(pathway)))
print("measure: " + str(round(coverage(pathway)/len(pathway)/indep(pathway), 2)))

"""### **Example 5 - Hedge Fund Applications**

As derived in the main paper, the Order Partitioning QUBO is of the form:

$$Q=a(T-2\sum_{j=1}^{n}q_{j}x_{j})^2 + b\sum_{i=1}^{m}(\sum_{j=1}^{n}p_{ij}(2x_{j}-1))^2$$

Where $T$ is the sum of the stock values, $q_{j}$ are the stocks and $p_{ij}$ are the risk factor matrix entries

Creating parameters for the Order Partitioning Problem.
"""

Stocks = ['A', 'B', 'C', 'D', 'E', 'F']
stock_vals = [300, 100, 100, 200, 200, 100]
#solutions S1 = {100,100,100,200} and S2 = {200,300} or S1 = {300,100,100} and S2 = {200,200,100}.
risk_factor_matrix = [[0.3, 0.1, 0.1, 0.2, 0.2, 0.1],
                      [0.4, 0.05, 0.05, 0.12, 0.08, 0.3],
                      [0.1, 0.2, 0.2, 0.3, 0.05, 0.05]]
T = sum(stock_vals)
n = 6 # number of stocks
m = 3 # number of risk factors

"""We create the Order Partitioning QUBO."""

x = Array.create('x', n, 'BINARY')
H1 = (T - 2*sum(stock_vals[j]*x[j] for j in range(n)))**2
H2 = sum(sum(risk_factor_matrix[i][j]*(2*x[j]-1)**2 for j in range(n)) for i in range(m))

# Construct hamiltonian
a = Placeholder("a")
b = Placeholder("b")
H = a*H1 + b*H2
model = H.compile()

# Generate QUBO
feed_dict = {'a': 2, 'b': 2}
bqm = model.to_bqm(feed_dict=feed_dict)

# Construct hamiltonian
a = Placeholder("a")
b = Placeholder("b")
H = a*H1 + b*H2
model = H.compile()

# Generate QUBO
feed_dict = {'a': 2, 'b': 2}
bqm = model.to_bqm(feed_dict=feed_dict)

"""We solve the QUBO using the Quantum Annealing Sampler."""

sampler = EmbeddingComposite(DWaveSampler())
sampleset = sampler.sample(bqm, num_reads=1000)
sample = sampleset.first # gets lowest energy sample

"""We display the solving details and solution."""

#Sorts samples by numbers to see which quadratic variables are 0 and 1
sampleKeys = list(sample.sample.keys())
def sortbynumber(str):
    return int(str[2:len(str)-1])
sampleKeys.sort(key = sortbynumber)
sortedSample = {i: sample.sample[i] for i in sampleKeys}
print(sortedSample)
print(sampleset.info)

# Converting the output binary variables to produce a valid output
Set_A = []
net_cost_A = 0
net_risk_1A = 0
net_risk_2A = 0
net_risk_3A = 0
Set_B = []
net_cost_B = 0
net_risk_1B = 0
net_risk_2B = 0
net_risk_3B = 0
keylist = list(sortedSample.keys())
for i in range(0, len(keylist)):
  if(sortedSample[keylist[i]] == 0):
    Set_A.append(Stocks[i])
    net_cost_A += stock_vals[i]
    net_risk_1A += risk_factor_matrix[0][i]
    net_risk_2A += risk_factor_matrix[1][i]
    net_risk_3A += risk_factor_matrix[2][i]
  else:
    Set_B.append(Stocks[i])
    net_cost_B += stock_vals[i]
    net_risk_1B += risk_factor_matrix[0][i]
    net_risk_2B += risk_factor_matrix[1][i]
    net_risk_3B += risk_factor_matrix[2][i]
print("Stock Partition: ", Set_A, Set_B)
print("Difference of Net Cost between Partition: ", net_cost_A-net_cost_B)
print("Difference of Net Risk between Partition: ", round((net_risk_1A+net_risk_2A+net_risk_3A)-(net_risk_1B+net_risk_2B+net_risk_3B),2))