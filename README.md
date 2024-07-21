# notification_slack_job

## 概要
クラウドワークス、ランサーズ、ココナラでキーワード検索に合致する新しい仕事が発生したら、スラックで通知する

## フォルダ構成
notification_slack_job
├── data
│   ├── cc.pkl
│   ├── cw.pkl
│   └── rc.pkl
├── src
│   ├── func_.py
│   ├── main.py
│   └── run.bat
├── README.md
└── requirements.txt

## 使い方
1. python3.11の仮想環境を'n_slack_nj'という名前で作成
2. main.pyの'KEYWORD'を設定(検索キーワード)
3. run.batをwindowsタスクスケジューラに設定(頻度は任意)