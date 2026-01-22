# 🚀 HR Onboarding Agentic Workflow - Quick Start Guide

Hướng dẫn nhanh để chạy agentic workflow tự động cho dự án HR Onboarding.

## 📁 Cấu Trúc Files Đã Tạo

```
.github/
├── agents/
│   └── hr-onboarding-orchestrator.agent.md  # Master orchestrator
├── instructions/
│   ├── skill-integration.instructions.md     # Cách sử dụng skills
│   └── task-workflow-automation.instructions.md  # Task lifecycle
├── prompts/
│   ├── agentic-workflow-executor.prompt.md   # Main executor
│   ├── execute-phase-1.prompt.md             # Phase 1 tasks
│   └── execute-phase-2.prompt.md             # Phase 2 tasks
├── skills/
│   ├── github-issues/                        # Issue management
│   ├── make-skill-template/                  # Create new skills
│   ├── microsoft-code-reference/             # Code patterns
│   └── microsoft-docs/                       # Documentation
└── workflows/
    └── agentic-workflow.yml                  # Workflow config
```

## 🎯 Cách Sử Dụng

### Option 1: Chạy Toàn Bộ Workflow

Trong VS Code, mở chat và gọi orchestrator:

```
@hr-onboarding-orchestrator Chạy toàn bộ workflow từ Phase 1 đến Phase 4
```

### Option 2: Chạy Từng Phase

**Phase 1 - Setup:**
```
@hr-onboarding-orchestrator Execute Phase 1: Project Setup
```

**Phase 2 - Backend:**
```
@hr-onboarding-orchestrator Execute Phase 2: Backend Implementation
```

**Phase 3 - API:**
```
@hr-onboarding-orchestrator Execute Phase 3: API Implementation
```

**Phase 4 - Testing:**
```
@hr-onboarding-orchestrator Execute Phase 4: Testing
```

### Option 3: Chạy Task Cụ Thể

```
@hr-onboarding-orchestrator Implement the Coordinator Agent using microsoft-code-reference skill
```

## 🔧 Sử Dụng Skills Riêng Lẻ

### GitHub Issues
```
Use skill: github-issues
Action: create
Title: "[Backend] New feature"
Labels: [backend]
```

### Microsoft Code Reference
```
Use skill: microsoft-code-reference
Query: "LangGraph StateGraph implementation"
```

### Microsoft Docs
```
Use skill: microsoft-docs
Query: "Azure Functions Python configuration"
```

## 📊 Theo Dõi Tiến Độ

Sau mỗi task, kiểm tra:

1. **Files created**: `ls -la backend/agents/`
2. **Syntax check**: `python -m py_compile backend/agents/*.py`
3. **GitHub issues**: Check repository issues

## ⚡ Quick Commands

| Action | Command |
|--------|---------|
| Start Phase 1 | `@hr-onboarding-orchestrator Execute Phase 1` |
| Create issue | `Use skill: github-issues` with Action: create |
| Lookup pattern | `Use skill: microsoft-code-reference` |
| Check docs | `Use skill: microsoft-docs` |
| Generate code | `@python-mcp-expert Create [component]` |

## 🎓 Workflow Automation Flow

```
┌─────────────────┐
│   User Request  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Orchestrator   │ ◄── Coordinates all skills
└────────┬────────┘
         ▼
┌─────────────────┐
│ github-issues   │ ◄── Creates tracking issue
└────────┬────────┘
         ▼
┌─────────────────┐
│ microsoft-code- │ ◄── Fetches code pattern
│ reference       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ python-mcp-     │ ◄── Implements code
│ expert          │
└────────┬────────┘
         ▼
┌─────────────────┐
│ pytest-coverage │ ◄── Writes tests
└────────┬────────┘
         ▼
┌─────────────────┐
│ github-issues   │ ◄── Closes issue
└─────────────────┘
```

## 🏆 48-Hour Sprint Timeline

| Hour | Phase | Skills Used |
|------|-------|-------------|
| 0-6 | Setup | github-issues |
| 6-16 | Backend | microsoft-code-reference, github-issues |
| 16-24 | API | microsoft-docs, github-issues |
| 24-36 | Integration | All skills |
| 36-44 | Testing | pytest-coverage, github-issues |
| 44-48 | Polish | github-issues (final) |

## 🔗 Related Files

- [Orchestrator Agent](.github/agents/hr-onboarding-orchestrator.agent.md)
- [Skill Integration Guide](.github/instructions/skill-integration.instructions.md)
- [Task Workflow](.github/instructions/task-workflow-automation.instructions.md)
- [Phase 1 Prompt](.github/prompts/execute-phase-1.prompt.md)
- [Phase 2 Prompt](.github/prompts/execute-phase-2.prompt.md)

---

**Bắt đầu ngay**: 
```
@hr-onboarding-orchestrator Khởi động Phase 1 - Tạo project structure và GitHub issues
```
