---
layout: about
title: about
permalink: /
description: Alejandro Montanez-Barrera — quantum computing researcher at Jülich Supercomputing Centre (JSC) working on QAOA, quantum optimization, and quantum hardware benchmarking.
subtitle: Institute for Advanced Simulation (IAS), Jülich Supercomputing Centre (JSC).

profile:
  align: right
  image: prof_pic.jpg
  image_circular: false # crops the image to make it circular
  more_info: >
    <p> Gebäude 16.4 </p>
    <p> Raum 308a </p>
    <p> Wilhelm-Johnen-Straße</p>
    <p> 52428 Jülich </p>
    <p>Forschungszentrum Jülich</p>

news: false  # includes a list of news items
latest_posts: false  # includes a list of the newest posts
selected_papers: true # includes a list of papers marked as "selected={true}"
social: true  # includes social icons at the bottom of the page
---

I am a postdoctoral researcher at the [Jülich Supercomputing Centre (JSC)](https://www.fz-juelich.de/en/ias/jsc) in Germany, working at the interface of quantum computing and high-performance computing. My research focuses on scalable methods for quantum optimization and quantum hardware benchmarking—especially protocols that reduce classical tuning overhead and enable fair cross-platform comparisons.

**Highlights**
- **LR-QAOA** validated on multiple platforms, including experiments up to **109 qubits** (*npj Quantum Information*).
- **Gate-based benchmarking at scale**: evaluated **28 QPUs from 6 vendors**, extending large-width analysis up to **156 qubits** (among the most extensive cross-platform studies I’m aware of).
- **Neutral-atom benchmarking**: first side-by-side benchmark (to my knowledge) of commercial QPUs from **QuEra** and **Pasqal**.

**Research interests**
- Quantum optimization (QAOA, parameter schedules, transfer learning)
- Quantum hardware benchmarking (cross-platform, width/depth scaling)
- Neutral-atom quantum computing and scalable MIS benchmarks
- HPC-enabled simulation and validation of quantum protocols

A key result of my work is **Linear-Ramp QAOA (LR-QAOA)**, showing that fixed parameter schedules can achieve high-quality solutions across diverse combinatorial optimization problems and serve as a practical depth-scaling benchmark. We validated LR-QAOA on multiple quantum processors, including experiments with up to **109 qubits**, and published the results in *npj Quantum Information*. I also work on benchmarking and performance evaluation at large width and depth, including gate-based benchmarking across **28 QPUs from 6 vendors**, extending the analysis up to **156 qubits**. In neutral-atom computing, I helped deliver (to my knowledge) the first side-by-side benchmark of two different commercial QPUs—**QuEra** and **Pasqal**—at meaningful scale.

I’m also committed to open-source: I’m an **OpenQAOA SDK maintainer** and contribute to the broader quantum software ecosystem (e.g., Qiskit, PennyLane, D-Wave Ocean). My work has been recognized with a Unitary Fund grant and multiple QHack/QDC competition awards.

I also developed a PennyLane tutorial on QUBO formulations for optimization: https://pennylane.ai/qml/demos/tutorial_QUBO

I hold a B.Sc. in electromechanical engineering (UPTC) and M.Sc./Ph.D. degrees in mechanical engineering from the University of Guanajuato (Ph.D. *summa cum laude*). With **16+ publications** spanning quantum computing, optimization, and machine learning, this multidisciplinary background helps me translate theory into practical methods for near-term quantum systems.

**Currently working on:** scalable benchmarks and parameter-transfer methods for quantum optimization, with an emphasis on fair comparisons across hardware modalities.

**Open to:** research collaborations, invited talks, and open-source contributions in quantum optimization and benchmarking.