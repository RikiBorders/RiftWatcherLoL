# Contributing to RiftWatcher

We're building a production-grade League of Legends statistics platform, and we're excited to have you contribute. Whether you're fixing bugs, building features, or owning subsystems, there's a place for you here.

---

## 🎯 What We're Looking For

We welcome contributors at all levels who share our commitment to quality and precision:

- **Bug fixes** that improve stability and accuracy
- **Feature development** for new capabilities to deliver more value to users
- **Performance optimization** across the stack
- **API enhancements** for broader integration
- **Documentation** that clarifies and improves the experience
- **Subsystem ownership** from contributors ready to take on larger domains

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized testing)
- Riot API key (for testing)

### Local Setup
1. Clone the repository
   ```bash
   git clone https://github.com/RikiBorders/RiftWatcherLoL.git
   cd RiftWatcherLoL
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run tests
   ```bash
   pytest
   ```

4. Test the API locally
   ```bash
   python src/rift_watcher_invoker/invoker.py
   ```

5. Or use Docker to spin up your own server
   ```bash
   docker build -t riftwatcher:latest .
   docker run --rm -p 5000:5000 riftwatcher:latest
   ```

---

## 🔑 Contribution Types

### Minor Contributions
Fix bugs, improve documentation, optimize small sections of code, or propose UI/UX improvements. These are excellent ways to get familiar with the codebase and make immediate impact.

### Feature Development
Help expand RiftWatcher's capabilities. Check the [ROADMAP](./ROADMAP.md) for planned features, or propose new ones that align with our vision. Feature contributions require:
- Clear problem statement and design
- Unit tests with >95% coverage
- Updated documentation

### Subsystem Ownership
As the product matures, we'll eventually need dedicated owners for key areas of the codebase. Subsystem owners are responsible for the health and direction of their domain, including:

- **Database Layer** – Manage schema optimization, query performance, and data integrity
- **API Server** – Own endpoint design, request handling, and response optimization
- **Data Processing** – Lead match extraction, stat calculation, and data transformation logic
- **Riot Integration** – Manage API adapters, rate limiting, and data sync strategies
- **Testing & CI/CD** – Build robust test suites and improve deployment pipelines

We're not yet at the point of needing subsystem owners, but if you're interested in taking on a larger role, let us know in the discussions or open an issue expressing your interest.

---

## 📋 Code Standards

We maintain high standards to keep RiftWatcher production-ready:

### Python Style
- Follow [PEP 8](https://pep8.org/) conventions
- Use type hints for function signatures
- Aim for **>95% test coverage** on new code
- Keep functions focused and under 50 lines when possible

### Testing Requirements
- All new features and bug fixes require tests
- Run `pytest` before submitting PRs
- Validate the server startup succeeds
- Manually validate modified API endpoints return expected responses
- Use descriptive test names that explain the scenario

### Documentation
- Add docstrings to all public functions and classes
- Update README or relevant docs if behavior changes
- Include inline comments for complex logic

### Commits
- Write clear, descriptive commit messages
- Reference issue numbers when applicable (e.g., `Fixes #42`)
- Squash all commits before submitting your PR

---

## 🔄 Pull Request Process

1. **Create a branch** from `main` with a descriptive name
   ```bash
   git checkout -b feature/match-stats-optimization
   ```

2. **Make your changes** following our code standards

3. **Test thoroughly**
   ```bash
   pytest
   python src/rift_watcher_invoker/invoker.py
   ```

4. **Open a PR** with:
   - Clear title and description
   - Reference to related issues
   - Summary of changes
   - Screenshots/outputs if applicable

5. **Address feedback** from code review

6. **Merge** once approved. Your contribution ships!

---

## 💬 Communication

- **Issues** – Use GitHub issues to report bugs, propose features, or discuss ideas
- **Discussions** – For broader conversations about architecture or strategy
- **Design** – See our [system design document](https://docs.google.com/document/d/1yzhuZO6NVqQyVGyzCaJOYMkEXU3-a3yOHOhM5iYEpOs/edit?tab=t.0) for architectural context

---

## 🎁 Contributor Recognition

- Your contributions appear in our [CHANGELOG](./CHANGELOG.md)
- Subsystem owners are credited in relevant module documentation
- Active contributors may be invited to the core team

---

## 📜 License

By contributing to RiftWatcher, you agree that your contributions will be licensed under the project's license.

---

## Questions?

Open an issue with the `question` label or start a discussion. We're here to help.

**Happy contributing!** ⚔️
