import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rho = 1.225     
g = 9.81
c = 0.2        
e = 0.8             

m_fuselage = 0.719
m_battery = 0.195
m_payload = 0.046 
wing_mass_per_m = 0.0227

V_range = np.arange(8, 14.5, 0.5)     
b_range = np.arange(1.2, 2.41, 0.1)      
inc_range = np.arange(0, 8.1, 1)           

V_thrust = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
T_available_data = np.array([
    5.6218, 4.790582, 4.082265, 3.478676, 2.964333,
    2.526038, 2.152547, 1.83428, 1.56307, 1.33196, 1.135022
])

V_drag = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
D_fuselage_data = np.array([
    0, 0.012315, 0.04926, 0.110835, 0.197041,
    0.307876, 0.443342, 0.603437, 0.788163, 0.997518, 1.231504
])

alpha_data = np.array([0, 2, 4, 6, 8])     

CL_2D_data = np.array([0.35, 0.55, 0.75, 0.89, 1.00])
CD_2D_data = np.array([0.018, 0.022, 0.030, 0.046, 0.070])

results = []

for V in V_range:
    for b in b_range:
        for inc in inc_range:

            S = b * c
            AR = b / c

            m_wing = wing_mass_per_m * b
            m_total = m_fuselage + m_battery + m_payload + m_wing
            W = m_total * g

            q = 0.5 * rho * V**2

            CL_2D = np.interp(inc, alpha_data, CL_2D_data)
            CD_2D = np.interp(inc, alpha_data, CD_2D_data)

            # 3D induced drag correction
            CDi = CL_2D**2 / (np.pi * e * AR)
            CD_total_wing = CD_2D + CDi

            L = q * S * CL_2D
            D_wing = q * S * CD_total_wing

            D_fuselage = np.interp(V, V_drag, D_fuselage_data)
            D_total = D_wing + D_fuselage

            T_available = np.interp(V, V_thrust, T_available_data)

            power_required = D_total * V

            CL_CD = L / D_total

            lift_margin = L / W
            thrust_margin = T_available / D_total

            feasible = lift_margin >= 1 and thrust_margin >= 1

            results.append({
                "V_mps": V,
                "wingspan_m": b,
                "aspect_ratio": AR,
                "incidence_deg": inc,
                "wing_area_m2": S,
                "mass_kg": m_total,
                "weight_N": W,
                "lift_N": L,
                "drag_N": D_total,
                "thrust_available_N": T_available,
                "power_required_W": power_required,
                "CL_CD": CL_CD,
                "lift_margin": lift_margin,
                "thrust_margin": thrust_margin,
                "feasible": feasible
            })

df = pd.DataFrame(results)
feasible_df = df[df["feasible"] == True].copy()

if feasible_df.empty:
    print("No feasible designs found. Check CL/CD data or design ranges.")
    exit()

best_endurance = feasible_df.loc[feasible_df["power_required_W"].idxmin()]

# Best cruise efficiency = maximum CL/CD
best_efficiency = feasible_df.loc[feasible_df["CL_CD"].idxmax()]


print("\nBest endurance design:")
print(best_endurance)

print("\nBest aerodynamic efficiency design:")
print(best_efficiency)

df.to_csv("all_design_results.csv", index=False)
feasible_df.to_csv("feasible_design_results.csv", index=False)

print("\nCSV files saved:")
print("- all_design_results.csv")
print("- feasible_design_results.csv")

plt.figure()
plt.scatter(
    feasible_df["wingspan_m"],
    feasible_df["incidence_deg"],
    c=feasible_df["power_required_W"]
)
plt.xlabel("Wingspan [m]")
plt.ylabel("Incidence [deg]")
plt.title("Power Required vs Wingspan and Incidence")
plt.colorbar(label="Power Required [W]")
plt.grid(True)
plt.savefig("power_vs_wingspan_incidence.png", dpi=300)


plt.figure()
plt.scatter(
    feasible_df["wingspan_m"],
    feasible_df["incidence_deg"],
    c=feasible_df["CL_CD"]
)
plt.xlabel("Wingspan [m]")
plt.ylabel("Incidence [deg]")
plt.title("Cruise Efficiency L/D vs Wingspan and Incidence")
plt.colorbar(label="L/D")
plt.grid(True)
plt.savefig("ld_vs_wingspan_incidence.png", dpi=300)


plt.figure()
plt.scatter(
    feasible_df["V_mps"],
    feasible_df["power_required_W"]
)
plt.xlabel("Cruise Speed [m/s]")
plt.ylabel("Power Required [W]")
plt.title("Power Required Across Feasible Cruise Speeds")
plt.grid(True)
plt.savefig("power_vs_speed.png", dpi=300)


plt.figure()
plt.scatter(
    feasible_df["V_mps"],
    feasible_df["CL_CD"]
)
plt.xlabel("Cruise Speed [m/s]")
plt.ylabel("L/D")
plt.title("Cruise Efficiency Across Feasible Cruise Speeds")
plt.grid(True)
plt.savefig("ld_vs_speed.png", dpi=300)


plt.show()