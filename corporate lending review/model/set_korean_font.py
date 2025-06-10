import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# 한글 폰트 경로 설정
if platform.system() == 'Windows':
    font_path = "c:/WINDOWS/Fonts/LG_SMART_UI-REGULAR.TTF"
elif platform.system() == 'Darwin':  # Mac
    font_path = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
else:  # Linux
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

# 폰트 등록
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)
plt.rcParams['axes.unicode_minus'] = False

print(f"✅ 설정된 한글 폰트: {font_name}")
