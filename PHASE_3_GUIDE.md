# 🎯 Phase 3: Azure Setup & Integration - HƯỚNG DẪN ĐẦY ĐỦ

## 📊 Current Status

✅ Phase 1: Project Setup - **COMPLETE**  
✅ Phase 2: Backend Agents - **COMPLETE**  
🔄 **Phase 3: Azure Setup & API Integration - IN PROGRESS**  
⏳ Phase 4: Testing & Demo - PENDING

---

## 🚀 Quick Setup (Chọn 1 trong 2 cách)

### Cách 1: Setup Tự Động (Khuyến nghị - 5 phút)

```bash
# Chạy script tự động
./scripts/quick-setup-azure.sh
```

Script sẽ tự động:
- ✅ Tạo Resource Group `hr-onboarding-rg`
- ✅ Tạo Cosmos DB (FREE tier)
- ✅ Tạo Azure Functions
- ✅ Tạo file `.env` với credentials
- ✅ Cấu hình tất cả settings

### Cách 2: Setup Có Tương Tác (Tùy chỉnh)

```bash
# Chạy script interactive để chọn tên resources
./scripts/setup-azure.sh
```

Bạn có thể tùy chỉnh:
- Tên Resource Group
- Location (khuyên dùng `southeastasia`)
- Tên các resources

---

## 📋 Chi Tiết Setup

### 1. Prerequisites

**Đã cài đặt:**
- ✅ Azure CLI (version 2.75.0)
- ✅ Azure account (logged in as tuanhoang.nguyen@dxc.com)

**Cần cài thêm:**
```bash
# Azure Functions Core Tools
brew tap azure/functions
brew install azure-functions-core-tools@4

# Python dependencies
cd backend
pip install -e ".[dev]"
```

### 2. Chạy Setup

```bash
# Option A: Quick setup (non-interactive)
./scripts/quick-setup-azure.sh

# Option B: Interactive setup (customize names)
./scripts/setup-azure.sh
```

**Thời gian:** 3-5 phút (Cosmos DB tạo hơi lâu)

### 3. Verify Setup

```bash
# Test connection và dependencies
./scripts/test-azure-setup.sh
```

Kết quả mong đợi:
```
✅ Test 1: Cosmos DB Connectivity - Passed
✅ Test 2: Azure Functions Core Tools - Passed
✅ Test 3: Python Dependencies - Passed
✅ Test 4: Create Test Record - Passed
✅ Test 5: Deployment Readiness - Passed
```

---

## 🧪 Local Development

### Start Local Server

```bash
cd backend
func start
```

Kết quả:
```
Functions:
  create_onboarding: [POST] http://localhost:7071/api/onboarding/create
  get_onboarding: [GET] http://localhost:7071/api/onboarding/{id}
  update_task: [PUT] http://localhost:7071/api/onboarding/{id}/task/{task_id}
  list_onboarding: [GET] http://localhost:7071/api/onboarding/list
  get_task_details: [GET] http://localhost:7071/api/onboarding/{id}/task/{task_id}
```

### Test API Endpoints

**1. Create Onboarding:**
```bash
curl -X POST http://localhost:7071/api/onboarding/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nguyen Van A",
    "role": "Software Engineer",
    "department": "Engineering",
    "start_date": "2026-02-01",
    "manager_id": "mgr-001"
  }'
```

**Response:**
```json
{
  "status": "success",
  "onboarding_id": "nh-1737619200",
  "message": "Onboarding workflow started",
  "state": {
    "new_hire_name": "Nguyen Van A",
    "current_phase": "pre_onboarding",
    "tasks": [
      {
        "id": "it-email",
        "title": "Create email account",
        "status": "completed",
        ...
      }
    ]
  }
}
```

**2. Get Status:**
```bash
curl http://localhost:7071/api/onboarding/{onboarding_id}
```

**3. Update Task:**
```bash
curl -X PUT http://localhost:7071/api/onboarding/{id}/task/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

---

## 🌐 Deploy to Azure

### Deploy Function App

```bash
cd backend

# Get your function app name from azure-resources.txt
FUNCTION_APP=$(grep "Function App:" ../azure-resources.txt | cut -d: -f2 | xargs)

# Deploy
func azure functionapp publish $FUNCTION_APP
```

### Get Production URL

```bash
az functionapp show \
  --name $FUNCTION_APP \
  --resource-group hr-onboarding-rg \
  --query defaultHostName -o tsv
```

### Test Production Endpoint

```bash
FUNCTION_URL="https://$(az functionapp show --name $FUNCTION_APP --resource-group hr-onboarding-rg --query defaultHostName -o tsv)"

curl -X POST $FUNCTION_URL/api/onboarding/create \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","role":"Engineer","start_date":"2026-02-01"}'
```

---

## 📁 Files Created

```
├── AZURE_SETUP_GUIDE.md          # Hướng dẫn chi tiết
├── QUICKSTART_AZURE.md           # Quick start 5 phút
├── azure-resources.txt           # Thông tin resources
├── backend/
│   └── .env                      # Credentials (KHÔNG commit!)
└── scripts/
    ├── setup-azure.sh            # Interactive setup
    ├── quick-setup-azure.sh      # Quick setup
    └── test-azure-setup.sh       # Test script
```

---

## 💰 Chi Phí

**FREE TIER (Không tốn tiền):**

| Resource | Free Tier | Usage | Cost |
|----------|-----------|-------|------|
| Cosmos DB | 1000 RU/s, 25GB | 400 RU/s, <1GB | **$0** |
| Azure Functions | 1M executions | <10K/month | **$0** |
| Storage | 5GB | <100MB | **$0** |
| **Total** | | | **$0/month** |

---

## 🔧 Troubleshooting

### Issue 1: "az command not found"
```bash
brew install azure-cli
```

### Issue 2: "Not logged in to Azure"
```bash
az login
```

### Issue 3: "func command not found"
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

### Issue 4: "Module not found" errors
```bash
cd backend
pip install -e ".[dev]"
```

### Issue 5: Cosmos DB connection timeout
```bash
# Wait 2-3 minutes for Cosmos DB to be fully provisioned
# Then run test again
./scripts/test-azure-setup.sh
```

### Issue 6: Port 7071 already in use
```bash
# Kill existing func process
pkill -f "func start"

# Or use different port
func start --port 7072
```

---

## ✅ Phase 3 Completion Checklist

Hoàn thành các bước sau để chuyển sang Phase 4:

- [ ] Azure CLI installed and logged in
- [ ] Run `./scripts/quick-setup-azure.sh` successfully
- [ ] File `backend/.env` created with credentials
- [ ] Run `./scripts/test-azure-setup.sh` - all tests pass
- [ ] Azure Functions Core Tools installed
- [ ] Dependencies installed: `pip install -e ".[dev]"`
- [ ] Local server starts: `func start` works
- [ ] API endpoints respond correctly
- [ ] Test create onboarding works
- [ ] Cosmos DB stores data correctly
- [ ] Deploy to Azure successful
- [ ] Production endpoint works

---

## 📚 Next Steps

### After Phase 3 Complete:

**Immediate:**
1. ✅ Test all API endpoints locally
2. ✅ Deploy to Azure Functions
3. ✅ Test production endpoints

**Phase 4 (Testing & Demo):**
1. Create demo scenarios
2. Record demo video
3. Prepare presentation slides
4. Create test dataset
5. Run integration tests

---

## 📖 Documentation Links

- [Azure Setup Guide](AZURE_SETUP_GUIDE.md) - Chi tiết đầy đủ
- [Quick Start](QUICKSTART_AZURE.md) - Bắt đầu nhanh 5 phút
- [Phase 1 Complete](PHASE_1_COMPLETE.md) - Project setup
- [Techno-Thon Guide](techno_thon_complete_guide.md) - Hướng dẫn hackathon

---

## 🆘 Support

**Có vấn đề?**

1. Kiểm tra [Troubleshooting](#-troubleshooting)
2. Chạy test: `./scripts/test-azure-setup.sh`
3. Xem logs: `func start` và check terminal output
4. Kiểm tra Azure Portal: https://portal.azure.com

**Logs:**
```bash
# Local logs
func start --verbose

# Azure logs
func azure functionapp logstream $FUNCTION_APP
```

---

## 🎉 Ready for Phase 4?

Khi tất cả checklist đã hoàn thành:
```bash
# Create Phase 3 completion marker
echo "✅ Phase 3 completed: $(date)" >> PHASE_3_COMPLETE.md
git add PHASE_3_COMPLETE.md
git commit -m "Complete Phase 3: Azure Setup & Integration"
```

**Tiếp theo:** [Phase 4 - Testing & Demo Guide](PHASE_4_GUIDE.md)
