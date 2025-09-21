# Karn.ai: Commander AI Simulation & Ranking Platform - Warp Context

## Project Overview
Karn.ai is a sophisticated, microservice-based AI simulation system designed specifically for Magic: The Gathering's Commander (EDH) format. This is a learning project focused on building advanced AI agents that can simulate 4-player Commander pods, train using reinforcement learning, and evaluate deck strategies.

## Key Project Goals
- **Primary**: Simulate 4-player Magic: The Gathering Commander games using AI agents
- **AI Training**: Implement reinforcement learning (PPO, A2C) with reward shaping and Bayesian convergence
- **Deck Analysis**: Evaluate deck performance based on strategic tags and win condition alignment
- **Educational**: Full replay system for understanding AI decision-making and game strategy
- **Community**: Support distributed simulation across volunteer compute clients

## Current Development Phase
This is a **Proof of Concept** project currently in early development phases:

### Phase 1: DECK & CARD DATA PIPELINE ⏳
- Load and parse raw Magic card data (Scryfall JSON)
- Build card Intermediate Representation (IR) generator
- Implement deck validation service for Commander format rules
- Target: 5 sample Commander decks for testing

### Phase 2: SIMULATION ENGINE CORE 🚧
- Build core game engine with full Magic rules implementation
- Turn structure, priority passing, combat mechanics
- Zone system (hand, library, battlefield, graveyard, exile, stack)
- Game end conditions and logging

## Architecture Overview

### Microservice Architecture (20+ planned services)
The system is designed as independently deployable microservices:

#### Core Simulation Services
- `simulation-engine`: Core rule-aware game engine
- `agent-hook`: Interface between game engine and AI decision system  
- `matchmaker`: Builds 4-player pods and dispatches simulations
- `replay-logger`: Captures complete game states and transitions

#### AI & Training Services
- `agent-service`: RLlib agent training and serving (PPO/A2C)
- `reward-shaping-agent`: Strategic utility and tag-aware feedback
- `bayesian-evaluator`: Convergence detection to halt redundant training
- `explanation-service`: Transparency for agent decision paths

#### Data Services
- `card-ir-generator`: Converts card JSON to structured IR with NLP
- `card-ir-registry`: Stores and indexes card Intermediate Representations
- `deck-service`: Commander format validation and deck management
- `value-index-service`: Gameplay efficiency vs market price analysis

#### Public Interface
- `ui-client`: Browser-based human vs AI gameplay
- `replay-viewer`: Interactive replay visualization with decision analysis
- `public-webpage`: EDHREC-style dashboard for meta analysis

## Technology Stack

### Languages & Frameworks
- **Python**: Primary for AI services, APIs, orchestration (current focus)
- **Rust**: Planned high-performance rules engine (future)
- **TypeScript/JavaScript**: Frontend and web interfaces
- **PyTorch + Ray/RLlib**: Distributed reinforcement learning
- **NumPy/Pandas**: Data processing and analysis

### Infrastructure & Data
- **Docker + Kubernetes**: Microservice orchestration (Azure AKS)
- **Databases**: PostgreSQL (logs), MongoDB (IR/metadata), Neo4j (interactions)
- **Message Bus**: Kafka for simulation coordination
- **Caching**: Redis for IR lookups and active pods
- **Observability**: Prometheus, Grafana, Loki, OpenTelemetry

### External APIs
- **Scryfall API**: Magic card metadata ingestion
- **TCGPlayer/CardMarket**: Market pricing data

## Development Environment

### File Structure
```
/docs/                    # Comprehensive documentation
├── architecture.md       # System design and service descriptions
├── tech-stack.md        # Technology choices and rationale
├── karn_poc_todo_list.md # Current development roadmap
├── Training/            # AI training documentation
├── Services/            # Individual service specifications
└── SRE/                 # Reliability and observability docs

README.md                # Project overview and getting started
LICENSE                  # MIT License
.github/                 # GitHub Actions CI/CD workflows
```

### Current Status
- **Documentation**: Extensive architectural planning complete
- **Implementation**: Early development - no code files yet in main branch
- **Focus**: Building foundational card data pipeline and simulation engine
- **Target**: Proof of concept with 5 Commander decks running 100+ simulations

## Magic: The Gathering Context
- **Format**: Commander (EDH) - 100-card singleton format with legendary commander
- **Gameplay**: 4-player multiplayer politics and strategy
- **Complexity**: Full Magic rules implementation required
- **Training Data**: Game replays, strategic tags, deck archetypes

## Learning Aspects (Python Focus)
This project offers excellent learning opportunities in:
- **AI/ML**: Reinforcement learning, reward shaping, Bayesian methods
- **Microservices**: Distributed systems, message queues, service orchestration
- **Data Engineering**: ETL pipelines, multiple database types, caching
- **Game Development**: Rules engines, state management, replay systems
- **DevOps**: Docker, Kubernetes, observability, CI/CD

## Development Workflow
1. **Current Phase**: Setting up card data pipeline and IR system
2. **Testing Strategy**: Focus on 5 sample decks for proof of concept
3. **Git Strategy**: Single repository for all microservices (monorepo approach)
4. **Documentation**: Extensive docs-driven development

## Important Notes
- **WOTC Compliance**: Follows Wizards of the Coast Fan Content Policy
- **Community-Focused**: Designed for educational and community benefit
- **Open Source**: MIT licensed for community contributions
- **Scalable Architecture**: Built for eventual public deployment

## Next Steps for Development
1. Implement card-ir-generator for Scryfall JSON parsing
2. Build deck-service for Commander validation
3. Create simulation-engine MVP with basic game loop
4. Integrate simple AI agents for automated gameplay
5. Establish replay logging and analysis system

This project represents a significant undertaking combining game AI, distributed systems, and Magic: The Gathering rules implementation - an excellent learning vehicle for advanced Python development, AI/ML, and system architecture.