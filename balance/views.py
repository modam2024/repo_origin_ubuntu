import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from django.http import HttpResponse

def get_data(symbol):
    dfStock = []

    for page in range(1, 21):
        print("==> 페이지 (" + str(page) + ")")
        url = "https://finance.naver.com/item/sise_day.naver?code={}&page={}".format(symbol, page)

        service = Service(
            executable_path="C:\\mySite\\chromedriver-win64\\chromedriver.exe"
        )
        # Headless 모드를 위한 옵션 설정
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        # ChromeDriver를 headless 모드로 시작합니다.
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        # 페이지의 소스를 가져옵니다.
        html = driver.page_source
        # BeautifulSoup 객체 생성
        soup = BeautifulSoup(html, "lxml")

        day_tr = soup.find_all("tr")
        ths = day_tr[0].find_all("th")  # 첫 번째 <tr> 태그 내의 모든 <td> 태그를 찾습니다.

        for i in range(1, len(day_tr)):
            tds = day_tr[i].select('td .tah, td .p10, td .p11')

            row_data = {}

            for j, td in enumerate(tds):
                row_data[ths[j].text] = td.text
            dfStock.append(row_data)

    dfStock_df = pd.DataFrame(dfStock)

    # NaN이 포함된 행 제거
    dfStock_df_cleaned = dfStock_df.dropna()

    # 전일비 컬럼에서 \n과 \t 제거
    dfStock_df_cleaned['전일비'] = dfStock_df_cleaned['전일비'].str.replace(r'[\n\t]', '', regex=True)

    # '날짜'와 '종가' 컬럼만을 선택하여 새로운 데이터프레임 생성
    df_date_price = dfStock_df_cleaned[['날짜', '종가']]

    # 드라이브 종료
    driver.quit()

    return df_date_price

def main_view(request):
  querydict = request.GET.copy()
  mylist= querydict.lists()

  for x in mylist:
     df_date_price = get_data(x[1][0])

  # DataFrame을 CSV 파일로 저장
  df_date_price.to_csv('date_price.csv', index=False)

  return HttpResponse("완료됐습니다.")  # No Content