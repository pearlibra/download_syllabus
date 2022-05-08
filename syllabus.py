from selenium import webdriver
import chromedriver_binary
import time
from selenium.webdriver.chrome import options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import os
import pw

try:
    options = webdriver.ChromeOptions()
    download_path = pw.download_path
    kibaco_user_id = pw.kibaco_user_id
    kibaco_pw = pw.kibaco_pw
    campussquare_user_name = pw.campussquare_user_name
    campussquare_pw = pw.campussquare_pw
    prefs = {
        "download.default_directory": download_path, 
        "download.directory_upgrade" : True
    }
    options.add_experimental_option('prefs', prefs)
    # options.add_argument('--headless')


    #----------kibacoへログイン----------
    driver = webdriver.Chrome(options=options)

    kibaco_login_url = 'https://kibaco.tmu.ac.jp/portal/site/ai2018kibansec'
    driver.get(kibaco_login_url)
    print('kibacoへログイン中...')
    time.sleep(5)

    login_button = driver.find_element(by=By.XPATH, value='//*[@id="Mrphs-choice"]/fieldset/a[1]')
    login_button.click()
    time.sleep(5)

    user_id_form = driver.find_element(by=By.XPATH, value='//*[@id="username"]')
    password_form = driver.find_element(by=By.XPATH, value='//*[@id="password"]')
    user_id_form.send_keys(kibaco_user_id)
    password_form.send_keys(kibaco_pw)
    driver.find_element(by=By.XPATH, value='/html/body/div/div/div/form/div[3]/button').click()
    time.sleep(5)

    #----------kibacoから情報取得----------
    # ウィンドウサイズの調整
    driver.set_window_size(1200, 1000)
    print('kibacoをから情報取得中...')
    #マイページに遷移
    driver.find_element(by=By.XPATH, value='//*[@id="topnav"]/li[1]/a[1]/span[2]').click()
    time.sleep(5)
    # 授業一覧へ遷移
    driver.find_element(by=By.XPATH, value='//*[@id="toolMenu"]/ul/li[3]/a').click()
    time.sleep(5)
    # 授業一覧から授業コードと授業カテゴリを取得
    elements = []
    count = len(driver.find_elements(by=By.CSS_SELECTOR, value='#currentSites > tbody > tr'))
    for i in range(count):
        class_code_xpath = '//*[@id="currentSites"]/tbody/tr[' + str(i+1) + ']/td[2]'
        detail_button_xpath = '/html/body/div[3]/div[9]/div[2]/main/div/div/div/div/form/div/table/tbody/tr[' + str(i+1) + ']/td[6]/span/a'
        class_name_xpath = '/html/body/div[3]/div[9]/div[2]/main/div/div/div/div/form/div/table/tbody/tr[' + str(i+1) + ']/td[3]/a'

        # 授業コードの取得
        class_code = driver.find_element(by=By.XPATH, value=class_code_xpath).text
        # 科目群を取得
        driver.find_element(by=By.XPATH, value=detail_button_xpath).click()
        time.sleep(5)
        class_category = driver.find_element(by=By.XPATH, value='//*[@id="dialog"]/div').text.split('\n')[0].replace('全学共通科目', '　')
        driver.find_element(by=By.XPATH, value='/html/body/div[8]/div[1]/button/span[1]').click()

        # 講義名を取得
        class_name = driver.find_element(by=By.XPATH, value=class_name_xpath).text

        elements.append([class_code, class_category, class_name])
    

    # ----------campussquareでシラバス検索----------
    campussquare_url = 'https://jjh.tmu.ac.jp/campusweb/campusportal.do'

    driver.get(campussquare_url)
    print('campussquareへログイン中...')
    time.sleep(5)

    # campussquareへログイン
    user_name_form = driver.find_element(by=By.XPATH, value='//*[@id="userNameInput"]')
    password_form = driver.find_element(by=By.XPATH, value='//*[@id="passwordInput"]')
    user_name_form.send_keys(campussquare_user_name)
    password_form.send_keys(campussquare_pw)
    driver.find_element(by=By.XPATH, value='//*[@id="LoginFormSimple"]/tbody/tr[3]/td/button[1]/span').click()
    time.sleep(5)

    # シラバスページへ
    driver.find_element(by=By.XPATH, value='//*[@id="tab-sy"]').click()
    time.sleep(5)

    # シラバスの検索
    iframe = driver.find_element(by=By.XPATH, value='//*[@id="main-frame-if"]')
    driver.switch_to.frame(iframe)

    syllabus = download_path + '/syllabus.pdf'

    print('シラバスの取得中...')
    for i in range(len(elements)):
        # 開講区分を選択
        radio = driver.find_element(by=By.XPATH, value='//*[@id="radio1"]')
        radio.click()

        # 授業コードを入力
        class_code_form = driver.find_element(by=By.XPATH, value='//*[@id="jikanwaricd"]')
        class_code_form.send_keys(elements[i][0])
        # 時間割決定ボタンを押す
        driver.find_element(by=By.XPATH, value='//*[@id="syInquirySearchInputForm"]/p/input[1]').click()
        time.sleep(5)
        # シラバスをダウンロード
        driver.find_element(by=By.XPATH, value='//*[@id="syInquirySearchInputForm"]/div[2]/input').click()
        time.sleep(5)
        # シラバスのファイル名を変更
        os.rename(syllabus, download_path + '/' + elements[i][2] + '.pdf')
        # 違う条件で探す
        driver.find_element(by=By.XPATH, value='//*[@id="syInquirySearchInputForm"]/div[3]/a').click()
        time.sleep(5)
    
    print('シラバスの取得が完了しました!')

except Exception as e:
    print(e)
finally:
    driver.quit()

