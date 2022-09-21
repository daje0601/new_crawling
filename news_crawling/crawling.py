from selenium.webdriver.common.by import By
from selenium import webdriver
from tqdm.auto import tqdm
import pandas as pd
import argparse
import logging
import time
import json
import os


def get_logger():
    logging.basicConfig(
        format='%(filename)s:%(lineno)d: %(message)s',
        level=logging.INFO)
    logger = logging.getLogger()
    return logger

def screen_shot(proseccor, name='Website.png'):
    proseccor.save_screenshot(name)
    
def get_info_one_page(df, target_category, kw):
    
    for i in range(len(target_category)):
        df = pd.concat(
            [
                df, 
                pd.DataFrame(
                    {
                        'keyword': [kw], 
                        'url': [str(target_category[i].get_attribute('href'))]
                    }
                )
            ]
        )
    df = df.reset_index(drop=True)
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page_numbers', type=int, default=500)
    parser.add_argument('--output_directory', type=str, default='data')
    parser.add_argument('--output_file_name', type=str, default='test.json')
    args = parser.parse_args()
    logger = get_logger()
    
    os.makedirs(args.output_directory, exist_ok=True)
    args.output_file_name = os.path.join(args.output_directory, args.output_file_name)
    
    with open('/Users/kds/Documents/search.json', 'r', encoding='utf8') as j:
        search_info = json.loads(j.read())
    
    url = search_info['url']
    logger.info(search_info)
    
    # add options
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(search_info['user-agent'])

    driver = webdriver.Chrome(
        "/Users/kds/Documents/chromedriver", 
        options=options, 
    )
    
    news_info_df = pd.DataFrame() # initialize news infomation dataframe
    for kw in search_info['keyword']:
        print(f"parsing keyword: {str(kw)}")
        # start
        driver.get(url)    
        # insert keyword
        elem = driver.find_elements(by=By.ID, value='query')[0]
        elem.send_keys(kw)
        # elem = driver.find_element_by_class_name('btn_submit')
        elem = driver.find_elements(by=By.CLASS_NAME, value='btn_submit')[0]
        elem.click()
        
        # find keyword tab
        tab_category = driver.find_elements(by=By.CLASS_NAME, value="menu")
        for i, c in enumerate(tab_category):
            if c.text == search_info['tab']:
                break
            else:
                continue
            
        # click keyword tab
        elem = driver.find_elements(by=By.XPATH, value=search_info['tab_xpath'])[0]
        elem.click()
        
        # find page numbers and news list
        logger.info('Parsing URLs...')
        tgt_page_nums = args.page_numbers
        
        for i in tqdm(range(tgt_page_nums)):
            time.sleep(1)
            news_categories = driver.find_elements(by=By.CLASS_NAME, value='info')
            time.sleep(2)
            news_categories = [c for c in news_categories if c.text == '네이버뉴스']
            time.sleep(2)
            news_info_df = get_info_one_page(news_info_df, news_categories, kw)
            
            if not i == (tgt_page_nums-1):
                # move to next page
                page_bottens = driver.find_elements(by=By.CLASS_NAME, value='btn_next')[0]
                time.sleep(1)
                try:
                    page_bottens.click()
                    time.sleep(3)
                except:
                    break
                
    print(news_info_df.tail())
    logger.info("Done")
    
    logger.info("Parsing elements...")
    success_num, fail_num = 0, 0
    modified_news_dict = {}
    for i, value in tqdm(news_info_df.T.items(), total=len(news_info_df)):
        keyword, url = value
        try:
            driver.get(url)
            time.sleep(2)
            title = driver.find_elements(by=By.CLASS_NAME, value='media_end_head_headline')[0].text
            elements = driver.find_elements(by=By.ID, value='dic_area')[0].text
            upload_time = driver.find_elements(by=By.CLASS_NAME, value="media_end_head_info_datestamp_time")[0].text
            company = driver.find_elements(By.CSS_SELECTOR, value='#ct > div.media_end_head.go_trans > div.media_end_head_top > a > img.media_end_head_top_logo_img.dark_type')[0].get_attribute("title")
            modified_news_dict[str(i)] = {
                "keyword": keyword, 
                "title": title, 
                "time": upload_time,
                "company": company,
                "url": url, 
                "contents": elements
            }
            
            with open(args.output_file_name, 'w', encoding='utf8') as j:
                json.dump(modified_news_dict, j, ensure_ascii=False, indent=4, sort_keys=False)
            success_num += 1
            
        except:
            logger.info(f"{url} is not validable")
            fail_num += 1
    logger.info("Done")
    
    # end
    logger.info(f"Succeed: {success_num}")
    logger.info(f"Failed: {fail_num}")
    
    driver.quit()

if __name__ == "__main__":
    main()