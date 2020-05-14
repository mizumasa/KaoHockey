# KaoHockey

Thank you for watching. 

This is a Hockey game "KaoHockey" with online meeting tools.

## Screenshot

![sample](https://github.com/mizumasa/KaoHockey/blob/master/kaohockey.jpg "サンプル")

# OS
* Windows 8.1 or later (not supported on Mac OS or Linux)

# Download
[Download zip](https://github.com/mizumasa/KaoHockey/releases/download/1.0/KaoHockey.zip)

# Other Required Software
* OBS Studio [Download](https://obsproject.com/ja/download)
* OBS Virtualcam 2.0.5 [Download](https://obsproject.com/forum/resources/obs-virtualcam.949/)

# Usage(in case Zoom)

1. Zoomでギャラリービューを使用する
   Use gallery view in zoom.

2. KaoHockey.exeを起動する
   Start KaoHockey.exe

3. Crop (Left,Top,Right,Bottom)のパラメーターを動かし、白枠がギャラリービューを囲むようにする
　 Move the crop (left, top, right, bottom) parameters so that the white frame surrounds the gallery view

4. 各種メニューを選択する
   Select various menus

5. Startボタンを押してゲームを開始する
   Press the Start button to start the game

6. 表示されたゲーム画面を、ウィンドウがZoomのギャラリービューに被らないように移動する
   Move the displayed game screen so that the window does not overlap Zoom's gallery view.

7. OBS Studio を起動する
   Start OBS Studio
   
8. 入力ソースにKaoHockeyのウィンドウを指定し、OBS Virtual Cameraプラグインを起動する
   Specify the KaoHockey window as the input source and start the OBS Virtual Camera plug-in
   
9. Zoom のカメラとしてOBS Cameraを認識させる（ゲーム画面が全プレーヤーに配信される）
   Recognize OBS Camera as Zoom camera (game screen is distributed to all players)

![sample](https://github.com/mizumasa/KaoHockey/blob/master/control.jpg "サンプル")

# Developer Requirement

* Windows 8.1 or later (not supported on Mac OS or Linux)
* Anaconda Python 3.5.0

# Required Python library

| name | version |
----|---- 
| dlib                      | 19.17 |
| pysimplegui               | 4.7.1 |
| opencv-python             | 4.1.0 |
| pillow                    | 5.4.1 |
| mss (install with pip) 	  | 5.1.0 |

# install
```
conda create -n py35 python=3.5
conda activate py35
pip install dlib pysimplegui opencv-python pillow mss
```
