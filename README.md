# WorldEdit for Endstone

This is a basic implementation of a WorldEdit-like plugin for the Endstone Minecraft server software.

## 설치 방법

1.  **프로젝트 빌드:**
    아직 `build` 패키지가 설치되지 않았다면, 먼저 설치해주세요.
    ```bash
    pip install build
    ```
    그 다음, 프로젝트의 루트 디렉토리(pyproject.toml 파일이 있는 곳)에서 다음 명령어를 실행하여 플러그인을 빌드합니다.
    ```bash
    python -m build
    ```
    이 명령어는 `dist` 폴더 안에 `.whl` 파일을 생성합니다. 이 파일이 Endstone 플러그인입니다.

2.  **플러그인 설치:**
    생성된 `.whl` 파일 (예: `dist/worldedit-0.1.0-py3-none-any.whl`)을 Endstone 서버의 `plugins` 폴더로 복사하거나 이동시킵니다. 또는 최신 릴리스에서 다운로드하세요.

3.  **서버 재시작:**
    Endstone 서버를 시작하거나 재시작하면 플러그인이 자동으로 로드됩니다.

## 사용 방법

1.  **선택 도구 받기:**
    게임에 접속하여 다음 명령어를 입력해 나무 도끼(선택 도구)를 받으세요.
    ```
    /wand
    ```

2.  **영역 선택하기:**
    *   **첫 번째 좌표 설정 (Pos1):** 나무 도끼를 손에 들고 원하는 블록을 **좌클릭**하세요. 채팅창에 "Position 1 set to (x, y, z)." 메시지가 나타납니다.
    *   **두 번째 좌표 설정 (Pos2):** 나무 도끼를 손에 들고 다른 위치의 원하는 블록을 **우클릭**하세요. 채팅창에 "Position 2 set to (x, y, z)." 메시지가 나타납니다.
    *   (선택) 또는 `/pos1`, `/pos2` 명령어를 사용하여 현재 서 있는 위치를 각 좌표로 설정할 수도 있습니다.

3.  **영역 채우기:**
    두 좌표가 모두 설정되면, 다음 명령어를 사용하여 선택된 직육면체 영역을 원하는 블록으로 채울 수 있습니다.
    ```
    /set <블록_이름>
    ```
    예를 들어, 선택된 영역을 돌(stone)으로 채우고 싶다면 다음처럼 입력하세요.
    ```
    /set minecraft:stone
    ```
    영역이 성공적으로 채워지면 "Area filled." 메시지가 나타납니다.
