from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os, pickle, csv

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
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

    return build('drive', 'v3', credentials=creds)

service = get_drive_service()

# 🔴 改成最上層資料夾 ID
ROOT_FOLDER_ID = '1PvbSMe3CdD_O0pPj1dRFiSvlvD4mrk5R'

results_rows = []

def scan_folder(folder_id, path):
    # 先列出這個資料夾底下的所有檔案 / 資料夾
    response = service.files().list(
        q=f"'{folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType, modifiedTime, parents)"
    ).execute()

    for item in response.get('files', []):
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            # 遞迴進子資料夾
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

# 開始遞迴
root_folder = service.files().get(
    fileId=ROOT_FOLDER_ID,
    fields="name"
).execute()

ROOT_FOLDER_NAME = root_folder['name']

scan_folder(ROOT_FOLDER_ID, ROOT_FOLDER_NAME)


# 輸出 CSV
with open('drive_videos.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["檔案名稱", "修改日期", "父層資料夾路徑", "父層資料夾連結"]
    )
    writer.writeheader()
    writer.writerows(results_rows)

print(f"完成，共輸出 {len(results_rows)} 筆影片資料")
