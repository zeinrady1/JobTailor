import os
from dotenv import load_dotenv
load_dotenv()

RESUME = {
    "name": "Zein Rady",
    "summary": (
        "Aerospace Engineering student at UC San Diego (3.65 GPA) specializing in Astrodynamics and Space Applications, "
        "with hands-on project experience in SolidWorks CAD, finite element analysis (FEA), MATLAB simulation, and "
        "high-powered rocket design. Proven ability to lead multidisciplinary engineering teams, deliver quantified "
        "structural results, and produce complete technical documentation across academic and professional environments."
    ),
    "contact": {
        "email": os.environ.get("CONTACT_EMAIL", ""),
        "phone": os.environ.get("CONTACT_PHONE", ""),
        "linkedin": "linkedin.com/in/zein-rady-a3475227b",
        "github": "github.com/zeinrady1",
        "website": "zeinrady.com",
    },
    "education": [
        {
            "school": "University of California, San Diego",
            "degree": "B.S. Aerospace Engineering, Specialization in Astrodynamics and Space Applications",
            "gpa": "3.65",
            "date": "Sep 2024 – Jun 2027",
            "coursework": "Orbital Mechanics, Spacecraft Guidance & Navigation, Flight Simulation Techniques, Advanced Fluid Mechanics, Signals & Systems, Linear Control, Thermodynamics, Probability & Statistics for Engineers",
        },
        {
            "school": "Irvine Valley College",
            "degree": "Associates in Mathematics, Physics, Natural Sciences, and Liberal Arts",
            "gpa": "3.70",
            "date": "Aug 2021 – Jun 2024",
            "coursework": "Calculus I–III, Physics I–III, SolidWorks CAD, MATLAB, C Programming",
        },
        {
            "school": "Certified SolidWorks CAD Design Associate",
            "degree": "Certification",
            "date": "Aug 2024",
        },
    ],
    "experience": [
        {
            "title": "Treasurer",
            "org": "Vertical Flight Society (VFS) @ UCSD",
            "date": "Oct 2025 – Jun 2026",
            "bullets": [
                "Manage and maintain comprehensive financial documentation, multi-semester budget forecasts, and expense reports supporting VFS engineering design and competition operations at UCSD.",
                "Coordinate end-to-end procurement workflows including vendor sourcing, purchase orders, delivery scheduling, and UCSD-compliant reimbursement processing for all club materials, components, and equipment.",
                "Collaborate with sub-team leads across aerodynamics, propulsion, and structures to strategically allocate funding and ensure milestone-driven engineering initiatives remain on schedule and within budget.",
            ],
        },
        {
            "title": "Behavioral Health Technician",
            "org": "Nyansa Learning Corporation",
            "date": "Jun 2025 – Sep 2025",
            "bullets": [
                "Delivered structured ABA-based (Applied Behavior Analysis) intervention sessions for children with developmental differences, implementing individualized programs to drive measurable growth in communication, social, and academic skills.",
                "Collected, recorded, and analyzed behavioral data across multiple clients in real time, identifying trends and adjusting intervention strategies to maximize learning outcomes and program effectiveness.",
                "Collaborated cross-functionally with licensed therapists, clinical supervisors, and family members to ensure alignment, consistency, and accurate electronic documentation across all client programs.",
            ],
        },
        {
            "title": "Lead Structural Designer",
            "org": "Freelance Engineering Project",
            "date": "Jun 2025 – Aug 2025",
            "bullets": [
                "Engineered 6 modular freestanding bleacher structures in SolidWorks, each independently rated to 5,000 lbs live load with a minimum factor of safety (FOS) of 4.5, achieving 30,000 lbs combined structural capacity.",
                "Performed finite element analysis (FEA) simulations covering stress, strain, and displacement under static and dynamic loading conditions to validate structural integrity and identify corrective design actions.",
                "Designed a relocatable treehouse-style spectator platform and 6-ft elevated deck with integrated bar area, optimizing for modular assembly, transport logistics, and on-site reconfiguration.",
                "Produced complete engineering documentation packages including SolidWorks CAD models, dimensioned technical drawings, FEA simulation reports, and build specifications delivered to contractors and architects.",
            ],
        },
        {
            "title": "Student Tutor",
            "org": "Berktree Learning Center",
            "date": "Jun 2024 – Sep 2024",
            "bullets": [
                "Provided personalized academic support in Calculus, Algebra, Geometry, English, ACT, and SAT prep.",
                "Developed tailored lesson plans using adaptive teaching methods to foster confidence and problem-solving skills.",
            ],
        },
        {
            "title": "Social Media Coordinator & Design Assistant",
            "org": "Youngfield USA",
            "date": "Feb 2023 – Jun 2024",
            "bullets": [
                "Developed and executed targeted campaigns across Instagram, Facebook, and TikTok, driving engagement and expanding brand presence.",
                "Used analytics to refine content strategy; collaborated with creative team on new collections and aesthetics.",
            ],
        },
        {
            "title": "Courtesy Clerk",
            "org": "Ralphs Grocery Company",
            "date": "Jun 2020 – Nov 2022",
            "bullets": [
                "Delivered efficient customer service while managing store operations, product restocking, and delivery coordination.",
            ],
        },
    ],
    "projects": [
        {
            "title": "Batch Least-Squares Orbit Determination",
            "subtitle": "MAE 182 – Spacecraft GNC, UCSD | Apr 2026 – Jun 2026",
            "bullets": [
                "Implemented an iterative batch least-squares estimator in MATLAB to estimate an 18-state vector (position, velocity, gravitational parameter μ, J2 oblateness coefficient, drag coefficient CD, and ground station biases) from simulated range and range-rate observations across a 5-hour tracking arc.",
                "Propagated the full state transition matrix (STM) numerically via ode45 at each iteration; algorithm converged to millimeter-level position accuracy within 5 correction passes.",
                "Generated pre/post-fit residual plots, RMS convergence curves, and a 1-σ position-error covariance ellipsoid to validate estimator performance and quantify uncertainty bounds.",
            ],
        },
        {
            "title": "Sequential Orbit Determination (Extended Kalman Filter)",
            "subtitle": "MAE 182 – Spacecraft GNC, UCSD | Final Exam Project, Jun 2026",
            "bullets": [
                "Implemented a sequential Extended Kalman Filter (EKF) in MATLAB to process range and range-rate observations one measurement at a time, using segment-by-segment state transition matrix (STM) propagation via ode45 for real-time orbit estimation.",
                "Applied the Joseph-form covariance update equation at each measurement step to preserve numerical stability, then back-propagated the final state estimate to epoch t₀ after filter convergence.",
                "Validated EKF solution against the batch least-squares reference by comparing 1-σ position-error covariance ellipsoids, confirming statistical consistency between sequential and batch estimation methods.",
            ],
        },
        {
            "title": "High-Powered Rocket – Proxima (RPL @ UCSD)",
            "subtitle": "Lead Design Engineer | Oct 2024 – Jun 2025",
            "bullets": [
                "Led a multidisciplinary engineering team through the complete design cycle of high-powered rocket Proxima: SolidWorks 3D CAD modeling, OpenRocket aerodynamic simulation, iterative structural optimization, 3D-printed component manufacturing, ground testing, and successful launch.",
                "Managed cross-functional coordination across propulsion, airframe structures, avionics, and recovery sub-teams, facilitating design reviews, resolving integration conflicts, and ensuring on-schedule milestone delivery.",
            ],
        },
        {
            "title": "Autonomous Quadcopter – DBVF @ UCSD",
            "subtitle": "Embedded Systems Team Member | Nov 2024 – Jun 2025",
            "bullets": [
                "Integrated Pixhawk 4 flight controller, GPS module, RF telemetry, and onboard environmental sensors into a custom quadcopter frame designed for autonomous wildfire-response navigation and real-time data collection.",
                "Diagnosed and resolved ESC (Electronic Speed Controller) calibration errors, power distribution faults, and telemetry dropout issues through systematic embedded systems debugging, restoring full vehicle functionality.",
            ],
        },
        {
            "title": "Freestanding Bleacher Structures (Freelance)",
            "subtitle": "Lead Structural Designer | Jun 2025 – Aug 2025",
            "bullets": [
                "Designed and modeled 6 custom SolidWorks structures rated to 5,000 lbs live load (FOS 4.5); performed FEA for stress, strain, and displacement validation.",
                "Delivered full engineering documentation package to contractors and architects.",
            ],
        },
    ],
    "skills": {
        "technical": [
            "MATLAB", "SolidWorks", "OpenRocket", "FEA Analysis", "3D CAD Modeling",
            "CAD Documentation", "3D Printing", "Arduino", "Soldering & Wiring",
            "C Programming", "Excel", "Data Analysis & Visualization", "GitHub",
            "Project Management", "Claude AI", "ChatGPT", "Structural Engineering",
        ],
        "soft": [
            "Leadership", "Cross-functional Collaboration", "Analytical Problem-Solving",
            "Attention to Detail", "Communication", "Adaptability", "Time Management",
            "Team Coordination", "Public Speaking", "Organization",
        ],
    },
}
