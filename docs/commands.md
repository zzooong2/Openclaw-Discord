# Fixed Korean Command List

The MVP accepts exact Korean commands only. Aliases are disabled at first, so every command below should match exactly after basic whitespace trimming.

## Mode Commands

| Spoken command | Action |
| --- | --- |
| `클로 온` | Turn voice control mode on |
| `클로 오프` | Turn voice control mode off |

## Confirmation Commands

| Spoken command | Action |
| --- | --- |
| `확인` | Execute the pending confirmation command |
| `취소` | Cancel the pending confirmation command |

## App Commands

| Spoken command | Action |
| --- | --- |
| `메모장 열어` | Open Notepad |
| `계산기 열어` | Open Calculator |
| `크롬 열어` | Open Chrome |
| `파일 탐색기 열어` | Open File Explorer |
| `메모장 닫아` | Request confirmation, then close Notepad |
| `계산기 닫아` | Request confirmation, then close Calculator |
| `크롬 닫아` | Request confirmation, then close Chrome |
| `파일 탐색기 닫아` | Request confirmation, then close File Explorer |
| `창 닫아` | Request confirmation, then close the active window |

## Mouse Movement Commands

| Spoken command | Action |
| --- | --- |
| `마우스 위로` | Move mouse up by the default step |
| `마우스 아래로` | Move mouse down by the default step |
| `마우스 왼쪽으로` | Move mouse left by the default step |
| `마우스 오른쪽으로` | Move mouse right by the default step |
| `마우스 조금 위로` | Move mouse up by a small step |
| `마우스 조금 아래로` | Move mouse down by a small step |
| `마우스 조금 왼쪽으로` | Move mouse left by a small step |
| `마우스 조금 오른쪽으로` | Move mouse right by a small step |
| `마우스 가운데로` | Move mouse to screen center |
| `마우스 왼쪽 위로` | Move mouse to top-left screen position |
| `마우스 오른쪽 위로` | Move mouse to top-right screen position |
| `마우스 왼쪽 아래로` | Move mouse to bottom-left screen position |
| `마우스 오른쪽 아래로` | Move mouse to bottom-right screen position |

## Click Commands

| Spoken command | Action |
| --- | --- |
| `왼쪽 클릭` | Left click |
| `오른쪽 클릭` | Right click |
| `더블 클릭` | Double click |

## Keyboard Shortcut Commands

| Spoken command | Action |
| --- | --- |
| `엔터` | Press Enter |
| `이스케이프` | Press Escape |
| `복사` | Press Ctrl+C |
| `붙여넣기` | Press Ctrl+V |
| `잘라내기` | Press Ctrl+X |
| `모두 선택` | Press Ctrl+A |
| `실행 취소` | Press Ctrl+Z |
| `다시 실행` | Press Ctrl+Y |
| `창 전환` | Press Alt+Tab |

## Text Input Command

| Spoken command shape | Action |
| --- | --- |
| `<짧은 문장> 입력` | Type the short Korean text before `입력` |

Text input is limited in MVP. The parser should reject empty text and overly long text.

## Out of Scope for MVP

The MVP must not implement arbitrary shell commands, file deletion, payment actions, credential entry automation, account management, system settings changes, or broad natural-language command guessing.

