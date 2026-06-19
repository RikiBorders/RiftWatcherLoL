# Roadmap

## Vision

RiftWatcher is a gaming analytics and coaching platform that transforms raw match history into actionable insight, social engagement, and AI-assisted improvement.

The goal is to evolve into a reusable analytics platform with multiple clients and interfaces built on top of shared capabilities.

---

# Principles

* Data before AI
* Capabilities before frontends
* Derived insight over dashboard complexity
* Stable interfaces over rapid rewrites
* Build only what unlocks the next layer

---

# Current State

## Infrastructure

* Portable Docker-based microservice deployment
* Service-oriented architecture
* Request / response contracts
* Structured logging and observability
* Source-controlled infrastructure

## Product

* Discord frontend
* Automated match ingestion foundation
* Player and match persistence

---

# Now (Highest Priority)

Focus: establish trustworthy analytics infrastructure.

## Match Intelligence

* [X] Complete historical match ingestion
* [X] Implement incremental polling
* [ ] Introduce ingestion retry + idempotency guarantees
* [ ] Add ingestion monitoring and alerting

## Data Platform

* [ ] Finalize match schema
* [ ] Finalize player performance schema
* [ ] Introduce aggregation pipelines
* [ ] Define canonical analytics models

## Developer Experience

* [ ] One-command local startup
* [ ] Architecture documentation
* [X] Contribution guide
* [ ] Local development dataset

## Success Indicators

* Reliable end-to-end ingestion
* Historical analytics available
* New contributor setup <5 minutes

---

# Next

Focus: convert events into player understanding.

## Analytics

* [ ] Performance trend analysis
* [ ] Rank progression tracking
* [ ] Session and streak detection
* [ ] Champion usage intelligence

## Social Layer

* [ ] Weekly recap generation
* [ ] Duo and rivalry statistics
* [ ] Shareable player summaries

## Identity

* [ ] Player profile cards
* [ ] Historical snapshots
* [ ] Personalized performance history

## Success Indicators

* Repeat usage within pilot servers
* Users returning for insight, not commands
* First externally shared outputs

---

# Later

Focus: build decision systems, not dashboards.

## AI Coaching

* [ ] Coaching objective generation
* [ ] Improvement recommendation engine
* [ ] Longitudinal player memory
* [ ] Explainable performance analysis

## Natural Language Analytics

* [ ] Ask questions over match history
* [ ] Trend explanation workflows
* [ ] Insight generation from analytics

## Evaluation

* [ ] Recommendation tracking
* [ ] User feedback collection
* [ ] Coaching quality metrics
* [ ] Experiment framework

## Success Indicators

* Recommendations grounded in analytics
* Measurable improvement loops
* Observable AI quality

---

# Platform Expansion

Focus: separate capabilities from interfaces.

## Capability Layer

* [ ] Introduce MCP-compatible interfaces
* [ ] Define stable tool contracts
* [ ] Standardize service boundaries

## Frontends

* [ ] Discord improvements
* [ ] Web client prototype
* [ ] Internal analytics console

## Open Ecosystem

* [ ] Public roadmap
* [ ] Standardized RFC process
* [ ] Contributor ownership model
* [ ] Community release cadence

## Success Indicators

* Multiple clients consuming shared capabilities
* External contributors merged
* Public release process

---

# Exploratory

High upside ideas that require validation before implementation.

* Predictive rank modeling
* Team synergy analysis
* Seasonal competitions
* Group intelligence
* API access
* Monetization experiments
* Coaching marketplace integrations

---

# Explicitly Not Planned

To preserve focus, these are intentionally out of scope for now.

* Generic chatbot features
* Real-time inference systems
* Multi-game expansion
* Fine-tuned models
* Mobile applications
* Growth optimization before retention

---

# Long-Term Goal

Build a platform that helps players answer:

> What should I do next?

while demonstrating strong ownership, extensibility, and maintainable engineering practices.
