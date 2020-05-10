# KaoHockey

Thank you for watching. 

This is a Hockey game "KaoHockey" with online meeting tools.

## Screenshot

![sample](https://github.com/mizumasa/KaoHockey/blob/master/kaohockey.jpg "サンプル")

# Requirement

* Windows 8.1 or later (not supported on Mac OS or Linux)
* Anaconda Python 3.6.0

# Required Python library

| name | version |
----|---- 
| dlib                      | 19.17 |
| pysimplegui               | 4.7.1 |
| opencv-python             | 4.1.0 |
| pillow                    | 5.4.1 |
| mss (install with pip) 	  | 5.1.0 |

# Usage(Zoomの場合)

1. Zoomの設定->一般を開き、「デュアルモニターの使用」にチェックを入れる
2. 新規ミーティングを開始し、参加者のギャラリービューを表示する
3. 以下のpythonを実行 

`python main.py`

4. Crop (Left,Top,Right,Bottom)のパラメーターを動かし、白枠がギャラリービューを囲むようにする
5. プルダウンメニューから四方の壁のゴールの設定をする（基本は TopがTeam1(青チーム) BottomがTeam2(赤チーム)）
6. Screen のチェックをONにしてゲーム開始
7. 表示されたゲーム画面を、ウィンドウがギャラリービューに被らないように移動し、Zoomの共有画面に設定する
   (この時、デュアルモニターの使用がONになっていないと、ギャラリービューが小さなサムネイル表示に変わってしまいます)

![sample](https://github.com/mizumasa/KaoHockey/blob/master/control.jpg "サンプル")

