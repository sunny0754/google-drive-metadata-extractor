# Google Drive API 認證資料提取流程筆記

---

# 第一層：問題類型（Problem Type）

## 類型
- OAuth 認證流程
- 本地快取驗證機制
- 物件有效性檢查

## 核心概念
- 憑證物件（creds）
- token 快取
- 有效期限檢查
- 若失效則重建

---

# 第二層：流程模板（Flow Template）

## 通用流程模型
1. 建立空物件
2. 檢查本地是否存在快取檔案
3. 若存在 → 讀取
4. 檢查物件是否有效
5. 若無效 → 重新認證
6. 儲存新物件
7. 使用物件建立服務

---

# 第三層：核心程式（Implementation）

<details>
<summary>點擊展開建立google api程式碼</summary>

```python

creds = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('drive', 'v3', credentials=creds)
```

<details>
<summary>點擊展開遞迴掃瞄子資料夾程式碼</summary>

```python
def scan_folder(folder_id, path):
  
    response = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType, modifiedTime, parents)"
    ).execute()

    for item in response.get('files', []):
        if item['mimeType'] == 'application/vnd.google-apps.folder':

            scan_folder(
                item['id'],
                f"{path}/{item['name']}"
            )
        else:
            if item['name'].lower().endswith(('.mp4', '.mov')):
                parent_url = f"https://drive.google.com/drive/folders/{folder_id}"

                results_rows.append({
                    "檔案名稱": item['name'],
                    "修改日期": item['modifiedTime'],
                    "父層資料夾路徑": path,
                    "父層資料夾連結": parent_url
                })
```
