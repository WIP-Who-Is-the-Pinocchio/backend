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

- 로컬 환경에 3306 포트 또는 MySQL 사용 중인지 포트 충돌 확인 필요
  - 3306 포트 프로세스 또는 컨테이너 확인 
  - brew로 설치한 MySQL 정지 cmd
    ```bash
    brew services stop mysql
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