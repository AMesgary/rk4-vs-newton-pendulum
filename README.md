# Pendulum Dynamics: Newton vs. RK4

This repository contains a real-time simple pendulum simulation written in Python using the Pygame library. The project serves as an interactive comparison between two different numerical methods for modeling dynamic systems.

## About the Project

The simulation explores the numerical equivalence between two distinct mathematical approaches:

* **Newtonian Analysis:** Calculates forces directly using Newton's second law and uses numerical integration to update the system state.
* **Differential Equations:** Solves the non-linear second-order differential equation of motion directly. The simulation uses the accurate Runge-Kutta 4th order (RK4) algorithm for this calculation.

Both models run simultaneously, allowing you to visually observe how the simple forward Euler method eventually diverges or introduces instability compared to the robust RK4 method, especially at larger time steps.

## The Mathematical Model

The differential equation governing the RK4 pendulum model is:

Where  is the angle,  is gravity,  is length,  is the damping coefficient, and  is mass.

## Requirements

To run the script, you will need Python 3 and the following library installed:

```bash
pip install pygame

```

## Controls

You can manipulate the physical properties of the system on the fly using the keyboard.

| Key(s) | Action | Range / Details |
| --- | --- | --- |
| **Space** | Pause or resume the simulation | N/A |
| **R** | Reset the simulation | N/A |
| **P** | Toggle the time plot | N/A |
| **Q** | Toggle the phase space plot | N/A |
| **Up / Down** | Adjust the damping coefficient | 0.0 - 0.5 |
| **G / H** | Adjust gravitational acceleration | 1.0 - 20.0 m/s² |
| **L / K** | Adjust pendulum length | 50 - 300 px |
| **M / N** | Adjust pendulum mass | 0.1 - 5.0 kg |
