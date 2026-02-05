# Contributing to Cody Foxy

Thank you for your interest in contributing to Cody Foxy! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a welcoming and inclusive environment for everyone.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cody-foxy.git
   cd cody-foxy
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pip install semgrep bandit
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Start development services**
   ```bash
   docker compose up db redis -d
   ```

5. **Run the applications**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates

### Creating a Branch

```bash
git checkout -b feature/my-new-feature
```

### Making Changes

1. Write your code
2. Add tests for new functionality
3. Update documentation if needed
4. Run the test suite

### Running Tests

**Backend:**
```bash
cd backend
pytest --cov=app
```

**Frontend:**
```bash
cd frontend
npm run test
npm run test:e2e  # End-to-end tests
```

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters

**TypeScript/JavaScript:**
- Use ESLint configuration
- Prefer TypeScript over JavaScript
- Use functional components in React

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance

**Examples:**
```
feat(scanner): add support for Rust language
fix(api): handle empty file uploads gracefully
docs(readme): update installation instructions
```

## Pull Request Process

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Push your changes**
   ```bash
   git push origin feature/my-new-feature
   ```

3. **Create a Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Provide a detailed description
   - Include screenshots for UI changes

4. **Code Review**
   - Address reviewer feedback
   - Keep discussions professional
   - Make requested changes promptly

5. **Merge**
   - Squash commits if needed
   - Ensure CI passes
   - Delete your branch after merge

## Reporting Issues

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, browser, versions)
- Screenshots or logs if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case / motivation
- Proposed implementation (optional)
- Mockups or diagrams (if applicable)

## Adding New Scanners

1. Create a new scanner service in `backend/app/services/`
2. Implement the scanner interface
3. Add language mapping in `LANGUAGE_SCANNERS`
4. Add tests for the new scanner
5. Update documentation

## Adding UI Components

1. Create component in `frontend/src/components/`
2. Add tests in `frontend/src/__tests__/`
3. Export from appropriate index file
4. Add Storybook story (if applicable)
5. Update component documentation

## Documentation

- Keep README.md up to date
- Document all public APIs
- Add JSDoc/docstrings for functions
- Include examples where helpful

## Questions?

- Open a GitHub Discussion
- Reach out via email: dev@codyfoxy.dev

Thank you for contributing! 🦊
