'''
利用pyomo优化求解组合权重
'''
import numpy as np
import pyomo.environ as pyo

def getphi(p, W, Wd):
    m, n = p.shape
    #create pyomo model
    model = pyo.ConcreteModel()
    model.M = pyo.Set(initialize=list(range(m)))
    model.N = pyo.Set(initialize=list(range(n)))

    #decision variables
    model.phi = pyo.Var(model.N, domain=pyo.NonNegativeReals)

    def obj_rule(model):
        F = 0
        for i in model.M:
            for j in model.N:
                F = F + np.power((W[j] - model.phi[j]) * p[i, j], 2) + np.power((Wd[j] - model.phi[j]) * p[i, j], 2)
        return F

    def phi_cons(model):
        return sum(model.phi[j] for j in model.N) == 1

    #objection function
    model.Obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    #constrains
    model.phi_cons = pyo.Constraint(rule=phi_cons)

    opt = pyo.SolverFactory('gurobi')    #利用gurobi求解约束
    solution = opt.solve(model)

    phi = np.array([pyo.value(model.phi[j]) for j in model.N])
    return phi
