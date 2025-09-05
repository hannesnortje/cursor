# Git Workflow & Branching Strategy

**Project:** AI Agent System with Cursor Integration  
**Last Updated:** September 4, 2025  
**Status:** Active Development

## Overview

This document defines the Git workflow and branching strategy for the AI Agent System project. We follow a **feature branch workflow** where each phase and major feature is developed in its own branch and merged to main upon completion.

## Branching Strategy

### Main Branches

#### `main` Branch
- **Purpose**: Production-ready code
- **Protection**: Only accepts merges from feature branches
- **Status**: Always stable and deployable
- **History**: Clean, linear history with meaningful commits

#### Feature Branches
- **Naming Convention**: `phase-{number}-{description}`
- **Examples**: 
  - `phase-1-foundation`
  - `phase-2-infrastructure` 
  - `phase-9-dynamic-agent-ecosystem`
- **Purpose**: Development of specific features or phases
- **Lifecycle**: Created from main → Developed → Tested → Merged to main → Kept for reference

## Current Branch Status

### ✅ Properly Branched Phases (Completed)
- **Phase 1**: `phase-1-foundation` ✅ (merged to main)
- **Phase 2**: `phase-2-infrastructure` ✅ (merged to main)
- **Phase 3**: `phase-3-coordinator` ✅ (merged to main)
- **Phase 4**: `phase-4-communication` ✅ (merged to main)
- **Phase 4.4**: `phase-4-4-testing-documentation` ✅ (merged to main)
- **Phase 5**: `phase-5-specialized-agents` ✅ (merged to main)

### 🔄 Retroactively Branched Phases (For Reference)
- **Phase 6**: `phase-6-llm-integration` (created from main history)
- **Phase 7**: `phase-7-advanced-features` (created from main history)
- **Phase 8**: `phase-8-dashboard` (created from main history)

### 🚧 Active Development Branches
- **Phase 9**: `phase-9-dynamic-agent-ecosystem` (current development)

## Git Workflow Process

### 1. Starting New Development

```bash
# 1. Ensure main is up to date
git checkout main
git pull origin main

# 2. Create new feature branch
git checkout -b phase-{number}-{description}

# 3. Start development
# ... make changes ...

# 4. Commit changes with conventional commits
git add .
git commit -m "feat: implement Phase X feature Y"
```

### 2. Development Process

```bash
# Make incremental commits
git add .
git commit -m "feat: add specific feature"
git commit -m "fix: resolve issue with feature"
git commit -m "docs: update documentation"

# Push branch to remote
git push origin phase-{number}-{description}
```

### 3. Completing Development

```bash
# 1. Final testing and cleanup
# ... run tests, fix issues ...

# 2. Update documentation
git add .
git commit -m "docs: update Phase X documentation"

# 3. Push final changes
git push origin phase-{number}-{description}

# 4. Create Pull Request (if using GitHub/GitLab)
# OR merge directly to main (current process)
```

### 4. Merging to Main

```bash
# 1. Switch to main
git checkout main

# 2. Merge feature branch
git merge phase-{number}-{description}

# 3. Push to remote
git push origin main

# 4. Keep feature branch for reference (DO NOT DELETE)
# git branch -d phase-{number}-{description}  # Only after final testing
```

## Commit Message Convention

We follow **Conventional Commits** specification:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples
```bash
git commit -m "feat: implement Phase 9.1 project-specific Qdrant databases"
git commit -m "fix: resolve circular import in dashboard API"
git commit -m "docs: update IMPLEMENTATION_PROGRESS.md with Phase 9 planning"
git commit -m "refactor: clean up dashboard system and remove redundant files"
```

## Branch Management

### Keeping Branches for Reference
- **DO NOT DELETE** feature branches until final testing is complete
- Branches serve as historical reference for each phase
- Useful for rollback if issues are discovered
- Can be used for hotfixes if needed

### Branch Cleanup (After Final Testing)
```bash
# Only after user has completed final testing
git branch -d phase-{number}-{description}  # Delete local branch
git push origin --delete phase-{number}-{description}  # Delete remote branch
```

## Current Development Status

### Active Branch: `phase-9-dynamic-agent-ecosystem`
- **Phase 9.1**: Project-Specific Qdrant Databases
- **Phase 9.2**: Enhanced AutoGen Integration
- **Phase 9.3**: Advanced Communication Features
- **Phase 9.4**: Predetermined Knowledge Bases

### Next Steps
1. Complete Phase 9.1 implementation
2. Test Phase 9.1 functionality
3. Commit and push Phase 9.1 changes
4. Continue with Phase 9.2
5. Repeat process for each sub-phase

## Best Practices

### 1. Branch Naming
- Use descriptive names: `phase-9-dynamic-agent-ecosystem`
- Include phase number for easy identification
- Use kebab-case for consistency

### 2. Commit Frequency
- Commit early and often
- Each commit should represent a logical unit of work
- Use meaningful commit messages

### 3. Testing
- Test each feature before merging
- Run comprehensive tests before final merge
- Document any testing requirements

### 4. Documentation
- Update documentation with each major change
- Keep IMPLEMENTATION_PROGRESS.md current
- Document any new processes or procedures

### 5. Code Quality
- Follow existing code style
- Add comments for complex logic
- Ensure all tests pass before merging

## Troubleshooting

### Common Issues

#### Merge Conflicts
```bash
# Resolve conflicts manually
git status  # See conflicted files
# Edit files to resolve conflicts
git add .
git commit -m "fix: resolve merge conflicts"
```

#### Accidentally Committed to Main
```bash
# Create feature branch from current state
git checkout -b phase-{number}-{description}
git push origin phase-{number}-{description}

# Reset main to previous state
git checkout main
git reset --hard HEAD~1  # or specific commit hash
git push origin main --force-with-lease
```

#### Lost Changes
```bash
# Recover from reflog
git reflog
git checkout <commit-hash>
git checkout -b recovery-branch
```

## Integration with Development Process

### Phase Development Workflow
1. **Planning**: Update IMPLEMENTATION_PROGRESS.md
2. **Branching**: Create feature branch
3. **Development**: Implement features with regular commits
4. **Testing**: Test functionality thoroughly
5. **Documentation**: Update all relevant documentation
6. **Merging**: Merge to main after completion
7. **Reference**: Keep branch for future reference

### Quality Gates
- All tests must pass
- Documentation must be updated
- Code must follow project standards
- No breaking changes without documentation

---

## Summary

This Git workflow ensures:
- **Clean History**: Linear, meaningful commit history
- **Traceability**: Each phase is clearly defined and trackable
- **Safety**: Branches are kept for reference and rollback
- **Quality**: Proper testing and documentation before merging
- **Collaboration**: Clear process for team development

The workflow supports our phased development approach while maintaining code quality and project organization.
