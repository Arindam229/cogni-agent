"""
Cognizance Festival Data
Contains all information about the festival, events, and activities.
"""

COGNIZANCE_DATA = """
# COGNIZANCE 2026 - FESTIVAL INFORMATION

## Basic Information
- **Name**: Cognizance
- **Edition**: Cognizance'2026
- **Institution**: Indian Institute of Technology Roorkee
- **Type**: Annual Technical Festival
- **Started**: 2003
- **Years of Existence**: 22 years
- **Organized By**: Student Community of IIT Roorkee
- **Location**: Roorkee, Uttarakhand, India
- **Dates**: 13th - 15th March 2026
- **Prize Pool**: 50 Lacs INR
- **Website**: https://www.cognizance.org.in
- **Registration**: https://www.cognizance.org.in/events

## What is Cognizance?
Cognizance is the annual technical fest of IIT Roorkee and represents the conjugation of the finest technical minds of the country. It serves as a national-level platform where innovation, engineering excellence, creativity, and problem-solving converge. The fest brings together students, researchers, developers, entrepreneurs, and industry professionals to compete, collaborate, and create solutions that address real-world technological and societal challenges.

## Theme 2026: Empyrean Technogenesis
**Empyrean Technogenesis** represents the rise of technology to its highest realm—where innovation is born, evolves, and transcends limits. It symbolizes the fusion of human intellect and advanced systems, shaping a future driven by limitless progress and elevated intelligence.

### Theme Symbolism:
- Empyrean signifies the highest plane of existence and excellence
- Technogenesis reflects the creation and evolution of technology
- Fusion of human cognition with advanced computational systems
- Continuous innovation beyond conventional boundaries

### Theme Focus Areas:
- Artificial Intelligence and Machine Learning
- Robotics and Automation
- Sustainable and Green Technologies
- Digital Systems and Cyber Intelligence
- Human-centered technological design

## Aim and Vision
**Primary Aim**: To provide a platform where ideas can speak out loud and technical skills are nurtured to help individuals reach the pinnacle of their intellectual potential.

**Core Objectives**:
- Promote innovation and technical excellence among students
- Encourage problem-solving using engineering and scientific approaches
- Bridge the gap between academia, industry, and society
- Expose participants to emerging technologies and real-world applications
- Foster leadership, teamwork, and entrepreneurial thinking

**Long-term Vision**: Cognizance envisions building a future-ready generation capable of leveraging technology responsibly, creatively, and ethically to drive progress at both national and global scales.

## Event Categories

### 1. SKY HIGH (Aerial Competitions)
- **Sky Maneuver**: Quadcopter designing and mapping challenge focusing on UAV control, navigation, and precision flying
- **Flight Fury**: RC plane challenge and airshow involving speed, stability, and aerial maneuvering

### 2. ROBOTICS
- **Armageddon** (FLAGSHIP EVENT): The ultimate robot battle competition featuring destructive combat robots. Manually controlled combat robots fight head-to-head inside a closed arena, focusing on mechanical strength, strategy, durability, and control
- **Plasma Pull**: Robot tug-of-war competition testing torque, grip, and power
- **Super Striker**: Robo-soccer event where autonomous or manual robots compete in a football-style arena
- **Nano Navigator**: Maze-solving micro mouse challenge emphasizing sensor integration and path optimization
- **Zengrip**: Pick-and-place robot challenge focused on precision gripping and manipulation
- **Trail Blaze**: Line-following robot competition testing speed and accuracy
- **Crawl-O-Tron**: Rope crawling robot event involving vertical mobility and mechanical design

### 3. COGITATION SUMMIT (Case Studies)
- **Solar Nexus**: Case study focused on empowering sustainable development through solar energy solutions
- **Prevenza**: Innovative approaches to combat and manage chronic diseases
- **Alpine Revival**: Sustainable tourism models for mountain and alpine communities
- **Intellectus**: Harnessing Artificial Intelligence for inclusivity and equity
- **Capital Choke**: Investigation into Delhi's air quality crisis and policy responses
- **Playwell**: Gamification strategies to address mental health challenges

### 4. BUSINESS AND FINANCE
- **Innovwave**: Bring your startup idea and pitch innovative business solutions
- **Bulls and Bears**: Virtual trading event simulating real stock market conditions
- **Prod-G**: Product management challenge focused on strategic thinking
- **Innoquest**: Consultancy-based case study competition

### 5. ALGO ARENA (Coding & Development)
- **Codify Rumble**: 1v1 competitive coding contest
- **BitByBit**: Full-stack hackathon focusing on complete product development
- **Agent X**: LLM-related event exploring AI agents and prompt systems
- **Scythe CTF**: Cybersecurity Capture The Flag competition
- **Blockathon**: Blockchain-based hackathon
- **Int'l Coding Challenge**: International-level online coding competition
- **Cosmic Classifier**: Machine learning challenge focused on planet classification
- **Architek**: City planning and architectural problem-solving event
- **FitFusion**: App development event focused on health and fitness solutions
- **Appnova**: UI/UX case study challenge
- **Snap Syntax**: HTML & CSS web design competition
- **Character-X**: Mascot and character design hackathon

### 6. OFF THE CUFF (Fun & Games)
- **Bridge-O-Mania**: Bridge building competition using ice-cream sticks
- **Grandmaster's Gambit**: Chess tournament
- **Trade Of Titans**: Superhero-themed auction event
- **Rubik's Ruckus**: Speed cubing competition
- **Wiki-Run**: Wikipedia hyperlink navigation race

### 7. E-SPORTS
- **BGMI**: Battle Royale mobile gaming competition
- **Valorant**: 5v5 tactical shooter tournament
- **Tekken 8**: Fighting game tournament
- **FIFA**: Football simulation gaming competition

### 8. IDEAZ (Departmental Events)
Department-wise paper presentation events across engineering and science departments

## Past Workshops
- Blockchain Development by Avalanche
- Cloud Computing Using Azure by Microsoft
- Solutions on AI/ML by Google
- AI/ML by Amazon (AWS)
- OneAPI by Intel
- Fusion360 by Autodesk
- DSA by GeeksforGeeks
- Rocket Modelling by ISRO - ITR
- Investment in Capital Market by CDSL
- Basics of Stock Market by SEBI
- Fashion Designing by NIFT Kangra
- App Development by Zoho
- Startup Innovation by Tides
- Geographic Information System by Bhoomicam
- Product Management by NextLeap

## Past Performers
- Arijit Singh
- Amit Trivedi
- Mohit Chauhan
- Jubin Nautiyal
- Sachin-Jigar
- Ritviz
- Papon
- Zakir Khan
- Harsh Gujral
- Rahul Dua
- DJ Olly Esse
- DJ Holy C
- Alok Gaur
- And Many More

## Impact and Reach
- **Participants**: Thousands of students from colleges and universities across India
- **Event Scale**: 200+ technical, managerial, and creative events across domains
- **National Reputation**: Recognized as one of the largest and most prestigious student-run technical festivals in India

## Core Message
Cognizance stands at the intersection of intellect and innovation. It empowers young minds to think beyond limits, build fearlessly, and shape a technologically advanced future driven by creativity, responsibility, and excellence.
"""


def get_cognizance_context() -> str:
    """Returns the complete Cognizance data as context for the LLM."""
    return COGNIZANCE_DATA


def get_structured_data() -> dict:
    """Returns structured data about Cognizance for programmatic access."""
    return {
        "festival_name": "Cognizance",
        "edition": "Cognizance'2026",
        "dates": "13th - 15th March 2026",
        "institution": "IIT Roorkee",
        "prize_pool": "50 Lacs INR",
        "theme": "Empyrean Technogenesis",
        "website": "https://www.cognizance.org.in",
        "registration_url": "https://www.cognizance.org.in/events",
    }
