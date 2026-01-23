# 🚀 Quick Start - Azure Setup (5 phút)

## Bước 1: Cài đặt Azure CLI (nếu chưa có)

```bash
brew install azure-cli
```

## Bước 2: Đăng nhập Azure

```bash
az login
```

Một cửa sổ browser sẽ mở ra để bạn đăng nhập.

## Bước 3: Chạy script tự động

```bash
./scripts/setup-azure.sh
```

Script sẽ:
- ✅ Tạo Resource Group
- ✅ Tạo Cosmos DB (FREE tier)
- ✅ Tạo Azure Functions
- ✅ Tạo file `.env` tự động

**Lưu ý**: Chọn location là `southeastasia` cho tốc độ tốt nhất từ VN.

## Bước 4: Kiểm tra setup

```bash
./scripts/test-azure-setup.sh
```

## Bước 5: Chạy local development

```bash
# Cài Azure Functions Core Tools
brew tap azure/functions
brew install azure-functions-core-tools@4

# Cài dependencies
cd backend
pip install -e ".[dev]"

# Chạy local server
func start
```

Kết quả mong đợi:
```
Functions:
  create_onboarding: [POST] http://localhost:7071/api/onboarding/create
  get_onboarding: [GET] http://localhost:7071/api/onboarding/{id}
  ...
```

## Bước 6: Test API

Mở terminal mới và test:

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

Nếu thành công, bạn sẽ nhận response JSON với thông tin onboarding.

## Troubleshooting

### Lỗi: "Azure CLI not found"
```bash
brew install azure-cli
```

### Lỗi: "Not logged in"
```bash
az login
```

### Lỗi: "func command not found"
```bash
brew tap azure/functions
brew install azure-functions-core-tools@4
```

### Lỗi: "Module not found"
```bash
cd backend
pip install -e ".[dev]"
```

## Chi phí

**MIỄN PHÍ** với Free Tier:
- Cosmos DB: 1000 RU/s free
- Azure Functions: 1M executions free
- Storage: 5GB free

## Tiếp theo?

- ✅ Setup xong? → Chuyển sang [Phase 3: Frontend & Integration](PHASE_3_GUIDE.md)
- ✅ Deploy production? → Chạy `func azure functionapp publish <app-name>`
- ✅ Xem resources? → Mở https://portal.azure.com

## Liên hệ

Có vấn đề? Tạo issue hoặc liên hệ team.
