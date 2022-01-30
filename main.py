
#########################################IMPORTS###########################################
import pandas
import requests
import numpy as np
from selenium import webdriver
import time
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from instascrape import *
import colorgram
from PIL import Image
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

import os
from os.path import join as opj

path = os.path.abspath(__file__)
curr_dir_path = os.path.dirname(path)

#######################################HARD-CODED#############################################
followsCol = 'followers'
colorCols = [f'color{i}' for i in range(1, 11)]
kMeansDfFileName = f'fullDataAfterKmeans.csv'
numberOfMainColorsNeeded = 10
user_name_1 = "cry_now_code_later"
password_1 = "*******"
user_name_2 = "code_now_cry_later"
password_2 = "*******"
####################################################################################

def post_links_crawler(words_to_search):
    '''Gets a list of words/acounts/hashtags to search and get the link to the posts on
    that particular page ---> return a list of the links
    using selenium '''

    driver = webdriver.Chrome()
    driver.get("https://www.instagram.com/")

    user_name = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    user_name.clear()
    password.clear()
    user_name.send_keys(user_name_2)
    password.send_keys(password_2)

    login_button = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
    not_now_bottun = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not Now')]"))).click()
    not_now_bottun_2 = WebDriverWait(driver, 10).until(
        expected_conditions.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Not Now')]"))).click()

    posts = []
    for word in words_to_search:
        search = WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
        search.clear()
        search.send_keys(word)
        time.sleep(1)
        search.send_keys(Keys.ENTER)
        search.send_keys(Keys.ENTER)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        #     driver.execute_script("window.scrollTo(0,100000);")

        links_to_posts = driver.find_elements(By.TAG_NAME, 'a')
        for link in links_to_posts:
            post = link.get_attribute('href')
            print(f"the post link {post}")
            if '/p/' in post:
                posts.append(post)
        time.sleep(15)

    return posts

####################################################################################

def make_and_save_df(data_links, file_to_save):
    '''gets a chunks 1,2,3...,8 of links to posts , and make a df from the data we want
    using the instascrape to take likes and comment and photos ,
     the mudole colorgram takes the 10 domminant colors in that photo
     and then saves the df '''
    session_id = '50837202909%3AwZz6MuC4fhu2yi%3A10'
    headers = {
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.57",
        "cookie": f"sessionid={session_id};"}
    # code above copied to bypass a error - sessionId is neccesery because instagram blocks me when i send
    # to many requests
    post_likes = []
    followers = []
    post_comments = []
    color1 = []
    color2 = []
    color3 = []
    color4 = []
    color6 = []
    color5 = []
    color7 = []
    color8 = []
    color9 = []
    color10 = []
    i = 1
    for url_to_post in data_links:
        try:
            print(f"iter no' : {i}")
            i = i + 1

            responce1 = requests.get(url_to_post, timeout=8)
            responce1.raise_for_status()
            print("------------responce succseeded--------------")
            post = Post(url_to_post)
            post.scrape(headers=headers)
            soup = BeautifulSoup(responce1.content, 'html.parser')
            # print(soup.prettify())

            comment_count = post.comments
            like_count = post.likes
            follower_count = post.followers
            image_url = post.display_url
            image = Image.open(requests.get(image_url, stream=True).raw)
            colors = colorgram.extract(image, 10)
            print("----------------Photo extracting succsseded-----------------")
            rgb_colors = []
            for color in colors:
                r = color.rgb.r
                g = color.rgb.g
                b = color.rgb.b
                rgb_colors.append((r, g, b))
            if len(rgb_colors) < 10:
                continue
            print("appending data - Done ")
            post_likes.append(like_count)
            followers.append(follower_count)
            post_comments.append(comment_count)
            color1.append(rgb_colors[0])
            color2.append(rgb_colors[1])
            color3.append(rgb_colors[2])
            color4.append(rgb_colors[3])
            color5.append(rgb_colors[4])
            color6.append(rgb_colors[5])
            color7.append(rgb_colors[6])
            color8.append(rgb_colors[7])
            color9.append(rgb_colors[8])
            color10.append(rgb_colors[9])
        except Exception as e:
            print(e)
            continue

    print("done all links for this chunk")
    df = pandas.DataFrame(
        {'likes': post_likes , 'followers': followers, 'comments': post_comments, 'color1': color1, 'color2': color2,
         'color3': color3,
         'color4': color4, 'color5': color5, 'color6': color6, 'color7': color7,
         'color8': color8, 'color9': color9, 'color10': color10})

    df.to_csv(file_to_save)

####################################################################################

def concatenate_dfs_to_one():
    dataFilesDirPath = opj(curr_dir_path, 'data_insta_files')
    dataToConcat = []
    for dataFile in os.listdir(dataFilesDirPath):
        if dataFile.startswith('data_insta'):
            dataToConcat.append(pandas.read_csv(opj(dataFilesDirPath, dataFile)))

    result_df = pandas.concat(dataToConcat)
    result_df.to_csv('instaDataFinal.csv', index=False)

####################################################################################

def cleanDataFrame():
    '''cleans duplicates , wrong values etc (DATA CLEANING)'''
    df = pandas.read_csv('instaDataFinal.csv')
    df.drop_duplicates(inplace=True)
    df.dropna(axis=0)
    df.drop(df[df.likes < 1].index, inplace=True)
    df.to_csv('instaDataCleanedAndReady.csv')

####################################################################################

'''
Clustering the RGB color tuples (R,G,B) to numbers between 0-9 
'''

# df = pandas.read_csv('instaDataCleanedAndReady.csv')
# df = df.copy(deep=True)
#
# allPossibleColors = np.zeros((len(colorCols) * df.shape[0], 3))
#
# matRowIdx = 0
# for rowIdx, row in df.iterrows():
#     for col in colorCols:
#         RGBCurr = re.findall("[0-9]+", row[col])
#         for colIdx in [0,1,2]:
#             allPossibleColors[matRowIdx, colIdx] = float(RGBCurr[colIdx])
#         matRowIdx +=1
#
# kmeans = KMeans(n_clusters=numberOfMainColorsNeeded)
# kmeans.fit(allPossibleColors)
#
# def predictUsingKmeans(x):
#     RGBCurr = re.findall("[0-9]+", x)
#     return kmeans.predict(np.array([int(RGBCurr[0]), int(RGBCurr[1]), int(RGBCurr[2])]).reshape(1,3))[0]

####################################################################################


# kmeans.cluster_centers_[idx] returns the actual cluster in the given idx
# for idx in range(0,10):
#     KMeans.cluster_centers_[idx]


df = pandas.read_csv(kMeansDfFileName)


featureCols = colorCols + ['comments', followsCol]
dataArray = df[featureCols].values
Y = df['likes'].astype(int).values

trainData = dataArray[:3000]
testData = dataArray[3000:]
Ytrain = Y[:3000]
Ytest = Y[3000:]

linearRegModel = LinearRegression()
linearRegModel.fit(trainData, Ytrain)

Logmodel = LogisticRegression()
Logmodel.fit(trainData, Ytrain)



