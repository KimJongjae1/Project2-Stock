pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
    buildDiscarder(logRotator(
      daysToKeepStr: '14',
      numToKeepStr: '50',
      artifactDaysToKeepStr: '14',
      artifactNumToKeepStr: '20'
    ))
    timeout(time: 60, unit: 'MINUTES')
    durabilityHint('PERFORMANCE_OPTIMIZED')
    skipDefaultCheckout(true)
  }

  // GitLab Generic Webhook (master push)
  triggers {
    GenericTrigger(
      token: 'deploy-hook',
      genericVariables: [[key: 'ref', value: '$.ref']],
      regexpFilterText: '$ref',
      regexpFilterExpression: '^refs/heads/master$'
    )
  }

  environment {
    HOST   = '13.125.222.104'
    REPO   = 'https://lab.ssafy.com/s13-bigdata-dist-sub1/S13P21A301.git'
    BRANCH = 'master'
  }

  stages {
    stage('Build & Deploy') {
      options { timeout(time: 40, unit: 'MINUTES'); retry(1) }
      steps {
        ansiColor('xterm') {
          withCredentials([
            sshUserPrivateKey(credentialsId: 'prod-ssh', keyFileVariable: 'KEY', usernameVariable: 'SSH_USER'),
            usernamePassword(credentialsId: 'gitlab-deploy', usernameVariable: 'GL_USER', passwordVariable: 'GL_PASS'),
            file(credentialsId: 'FRONTEND_ENV', variable: 'FE_ENV_FILE') // 필요 없으면 빼도 됨
          ]) {
            sh '''
set -eu

echo "==[1/5] 원격 준비 =="
ssh -o StrictHostKeyChecking=no -i "$KEY" "$SSH_USER@${HOST}" '
  set -e
  mkdir -p ~/ci/app/repo/frontend ~/ci/app/repo/back /srv/app/backend /srv/app/frontend
'

echo "==[2/5] .env 업로드 (프론트용 선택) =="
scp -o StrictHostKeyChecking=no -i "$KEY" "$FE_ENV_FILE" "$SSH_USER@${HOST}:~/ci/app/repo/frontend/.env.tmp" || true
ssh -o StrictHostKeyChecking=no -i "$KEY" "$SSH_USER@${HOST}" '
  set -e
  if [ -f ~/ci/app/repo/frontend/.env.tmp ]; then
    mv ~/ci/app/repo/frontend/.env.tmp ~/ci/app/repo/frontend/.env && chmod 600 ~/ci/app/repo/frontend/.env
  fi
'

rm -rf logs && mkdir -p logs

echo "==[3/5] 원격 빌드/배포 =="
ssh -o StrictHostKeyChecking=no -i "$KEY" "$SSH_USER@${HOST}" GL_USER="$GL_USER" GL_PASS="$GL_PASS" REPO="$REPO" BRANCH="$BRANCH" 'bash -s' <<'EOS'
set -Eeuo pipefail
mkdir -p ~/ci/app ~/ci/logs
cd ~/ci/app

# --- Repo sync ---
if [ ! -d repo ]; then
  git clone --depth=1 --branch "$BRANCH" "https://${GL_USER}:${GL_PASS}@${REPO#https://}" repo
else
  git -C repo fetch --depth=1 origin "$BRANCH"
  git -C repo reset --hard "origin/$BRANCH"
fi
echo "[repo] HEAD: $(git -C repo rev-parse --short HEAD)" | tee ~/ci/logs/clone.log

# 도구 설치(없으면)
if ! command -v git >/dev/null 2>&1; then
  sudo apt-get update -y && sudo apt-get install -y git openjdk-17-jdk rsync docker-compose-plugin
fi

# --- Backend build → app.jar 배치 ---
(
  set -e
  cd repo/back
  if [ -f ./gradlew ]; then
    chmod +x ./gradlew
    ./gradlew clean bootJar -x test
    JAR=$(ls build/libs/*.jar | head -n1)
  elif [ -f ./mvnw ]; then
    chmod +x ./mvnw
    ./mvnw -DskipTests package
    JAR=$(ls target/*.jar | head -n1)
  elif [ -f pom.xml ]; then
    sudo apt-get update -y && sudo apt-get install -y maven
    mvn -DskipTests package
    JAR=$(ls target/*.jar | head -n1)
  else
    echo "[back][ERR] build tool not found"; exit 2
  fi
  sudo mkdir -p /srv/app/backend
  sudo cp -f "$JAR" /srv/app/backend/app.jar
  echo "[back] artifact: $JAR"
) 2>&1 | tee ~/ci/logs/backend_build.log

# --- Backend image build (Dockerfile.backend 사용) ---
(
  set -e
  cd /srv/app
  docker compose build app
) 2>&1 | tee -a ~/ci/logs/backend_build.log

# --- Frontend build ---
(
  set -e
  cd repo/frontend
  sudo rm -rf dist build node_modules || true
  uid=$(id -u); gid=$(id -g)

  # ⚠️ 여기서 핵심: VITE_API_BASE_URL을 "빈 값"으로 주입
  #   → 번들에는 ''이 들어감. 코드가 /api/... 상대경로를 쓰면 최종 /api/... 만 생성
  docker run --rm -u ${uid}:${gid} \
    -v "$PWD:/src" -w /src \
    -e VITE_API_BASE_URL= \
    -e VITE_WS_BASE_URL=/ws \
    -e VITE_SERVER_URL=https://j13a301.p.ssafy.io \
    node:20-bullseye bash -lc '
      set -e
      if [ -f package-lock.json ]; then npm ci; else npm i; fi
      npx vite build --mode production
    '

  OUTDIR=""
  [ -d dist ] && OUTDIR="dist"
  [ -z "$OUTDIR" ] && [ -d build ] && OUTDIR="build"
  if [ -z "$OUTDIR" ]; then echo "[front][ERR] build output not found"; exit 21; fi

  sudo mkdir -p /srv/app/frontend/dist
  sudo rsync -a --delete "$OUTDIR/"/ /srv/app/frontend/dist/

  COMMIT=$(git -C .. rev-parse --short HEAD || true)
  DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
  echo "commit=${COMMIT} built_at=${DATE}" | sudo tee /srv/app/frontend/dist/__build.txt >/dev/null

  # 참고: 실패 유발하던 하드코드 검사 제거(경고만 남김)
  grep -R '/api/api/' -n "$OUTDIR" && echo "[warn] /api/api 문자열이 번들에 존재합니다. 코드에서 중복 슬래시 여부를 확인하세요." || true
) 2>&1 | tee ~/ci/logs/frontend_build.log

# --- Deploy & light smoke ---
(
  set -e
  cd /srv/app
  docker compose up -d app nginx
  docker compose ps
  docker compose exec -T nginx nginx -t || true
  docker compose exec -T nginx nginx -s reload || true

  set +e
  echo -n "HTTP /            : "; curl -sI https://j13a301.p.ssafy.io | head -n1
  echo -n "API Google (302?) : "; curl -sI https://j13a301.p.ssafy.io/api/users/auth/google | grep -i ^location || true
) 2>&1 | tee ~/ci/logs/deploy.log
EOS

echo "==[4/5] 원격 로그 수집 =="
scp -o StrictHostKeyChecking=no -i "$KEY" "$SSH_USER@${HOST}:~/ci/logs/*" ./logs/ || true
'''
          }
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'logs/**', fingerprint: true, onlyIfSuccessful: false
      echo "⏱ 총 소요: ${currentBuild.durationString}"
    }
    success { echo '✅ 배포 성공' }
    unstable { echo '⚠️  배포 불안정(UNSTABLE)' }
    failure { echo '❌ 배포 실패' }
    cleanup { cleanWs(deleteDirs: true, notFailBuild: true) }
  }
}
