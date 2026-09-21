# stock_check 배포 / 재시작

Mac에서 코드 수정 → GitHub `stock_check` → EC2 반영 → 서비스 재시작

`stock_monitor` 와 **다른 GitHub 저장소, 다른 폴더, 다른 포트, 다른 systemd** 입니다. 모니터 알람/설정 웹은 그대로 둡니다.

## 접속 정보

| 항목 | 값 |
|------|-----|
| 로컬 | `~/Programming/stock_check` |
| GitHub | `https://github.com/okm1011/stock_check.git` |
| 브랜치 | `main` |
| SSH | `ssh -i ~/Programming/stock_monitor_key.pem ec2-user@13.209.65.145` |
| 서버 경로 | `~/stock_check` (`/home/ec2-user/stock_check`) |
| 서비스 | `stock-check` |
| 웹 | `http://13.209.65.145:8090` |

모니터 설정 웹은 계속 `http://13.209.65.145:8080` 입니다.

> Mac SSH는 `./키.pem` / `/` 경로. Windows처럼 `.\` 쓰지 마세요.

---

## 모니터에 영향 있나?

**코드·DB·알람·8080 웹은 안 건드립니다.**

같은 EC2에서 프로세스만 하나 더 돕니다.

| | stock_monitor | stock_check |
|--|---------------|-------------|
| 폴더 | `~/stock_monitor` | `~/stock_check` |
| GitHub | `okm1011/stock_monitor` | `okm1011/stock_check` |
| 서비스 | `stock-monitor`, `stock-monitor-web` | `stock-check` |
| 포트 | 8080 | 8090 |

t3.micro 메모리가 작아서, 둘 다 켜 두면 CPU/RAM은 나눠 씁니다. 모니터가 자주 죽거나 서버가 느려지면 stock_check 쪽 폴링을 늘리거나 인스턴스를 키우면 됩니다. **git pull 한 쪽이 다른 쪽 코드를 덮어쓰지는 않습니다.**

---

## 0) 처음 한 번만 (clone)

서버에 `~/stock_check` 가 없을 때입니다. **이때는 git pull 이 아니라 clone** 입니다.

### AWS 보안 그룹

인바운드 **TCP 8090** 추가 (8080 넣을 때와 같음). 내 IP 또는 `0.0.0.0/0`.

### SSH 후

```bash
cd ~
git clone https://github.com/okm1011/stock_check.git
cd ~/stock_check
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

외부에서 웹을 열려면 `host` 를 바꿉니다.

```bash
nano ~/stock_check/config.yaml
```

```yaml
host: 0.0.0.0
port: 8090
```

저장: `Ctrl+O` Enter, 종료: `Ctrl+X`

systemd 등록:

```bash
sudo cp ~/stock_check/deploy/stock-check.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now stock-check
sudo systemctl status stock-check --no-pager
```

`Active: active (running)` 이면 브라우저: `http://13.209.65.145:8090`

---

## A. 그다음부터 코드 업데이트 (git pull)

### 1) Mac

```bash
cd ~/Programming/stock_check
git add .
git commit -m "변경 요약"
git push
```

(`unset GIT_ASKPASS` 후 push. Password는 GitHub 토큰)

### 2) 서버 SSH

```bash
ssh -i ~/Programming/stock_monitor_key.pem ec2-user@13.209.65.145
```

### 3) pull + 재시작 (SSH 안)

```bash
cd ~/stock_check
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart stock-check
sudo systemctl status stock-check --no-pager
```

`requirements.txt` 안 바꿨으면 `pip install` 은 건너도 됩니다.

웹만 안 바뀌면 모니터 재시작은 **하지 마세요.**

```bash
# 하지 말 것 (이번 배포와 무관)
# sudo systemctl restart stock-monitor
# sudo systemctl restart stock-monitor-web
```

---

## B. 서버만 다시 킬 때

```bash
sudo systemctl restart stock-check
sudo systemctl status stock-check --no-pager
journalctl -u stock-check -f
```

`status` 맨 아래 `(END)` 는 페이저입니다. **`q`** 로 나가세요.

---

## 한 줄 요약

**처음:** 서버에서 `git clone` → venv → `host: 0.0.0.0` → systemd `stock-check` → 보안그룹 8090  
**이후:** Mac `push` → 서버 `cd ~/stock_check && git pull` → `sudo systemctl restart stock-check`  
**모니터:** 그대로 둠 (`~/stock_monitor`, `:8080`)
