# WIP Server

## Requirements

- `Python` 3.11.5
- `Poetry` 1.6.1
- `FastAPI` 0.103.2
- `SQLAlchemy` 2.0.21


## Execution

### 필요 환경
1. Docker 설치
2. MySQL 이미지 다운로드
```bash
docker pull mysql:latest
```

### 실행

```bash
docker-compose up -d --build
```
- `Dev Swagger URL` - http://localhost:2309/docs


### 종료
```bash
docker-compose down
```

## Test
- 전체 API 테스트
    ```bash
    pytest src/tests
    ```
  
- Admin auth API 모듈 테스트
    ```bash
    pytest src/tests/test_admin_auth.py
    ```