from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup


# Initiate the browsers
driver  = webdriver.Chrome(ChromeDriverManager().install())
driver.get('https://www.birdieworld.com/1s48NSL7WCk=')
driver.implicitly_wait(15)
email = driver.find_element_by_id("user_email")
email.send_keys(input("Email: "))
password = driver.find_element_by_id("user_password")
password.send_keys(input("Password: "))
password.send_keys(Keys.RETURN)
driver.get('https://www.birdieworld.com/admin/shows?direction=desc&order=approved')
x = 1

#run flag script
flag = driver.find_element_by_xpath("/html/body/div/main/header/div[2]/form/input[3]")
flag.click()
driver.back()

while(True): 
    imdb = ""
    mpaa = ""
    rt = ""
    
    approval = driver.find_element_by_xpath("/html/body/div/main/section/table/tbody/tr[" + str(x) + "]/td[5]/a").text
    if (approval == "true"):
        break

    show = driver.find_element_by_xpath("/html/body/div/main/section/table/tbody/tr[" + str(x) +"]")
    show.click()

    flagged = driver.find_element_by_xpath("/html/body/div/main/section/dl/dd[20]").text

    if (flagged == "true"):
        x += 1
        driver.back()
        continue 
        
        
    
    # Get movie and year 
    movie = driver.find_element_by_xpath("/html/body/div/main/section/dl/dd[2]").text
    year = driver.find_element_by_xpath("/html/body/div/main/section/dl/dd[3]").text
    print("SEARCH FOR: " + movie + " " + year) 
    movie_split = movie.lower().split()
    movie_clean = ""
    for word in movie_split:
        for character in word: 
            if character.isalnum():
                movie_clean += character
        movie_clean += "-"
    movie_search = movie_clean + year
    
    try:
        # Open ReelGood
        movies_rg = requests.get("https://reelgood.com/movie/" + movie_search)
        rg_soup = BeautifulSoup(movies_rg.content, 'html.parser')
        # Get IMDb Rating
        imdb = rg_soup.find("div", {"title": "IMDb Rating"}).find("span", {"class": "css-xmin1q ey4ir3j3"}).text
        print(imdb)
        # Get MPAA Rating
        mpaa = rg_soup.find("span", {"title": "Maturity rating"}).text
        print(mpaa)
    except:
        try:
            movies_rg = requests.get("https://reelgood.com/show/" + movie_search)
            rg_soup = BeautifulSoup(movies_rg.content, 'html.parser')
            # Get IMDb Rating
            imdb = rg_soup.find("div", {"title": "IMDb Rating"}).find("span", {"class": "css-xmin1q ey4ir3j3"}).text
            print(imdb)
            # Get MPAA Rating
            mpaa = rg_soup.find("span", {"title": "Maturity rating"}).text
            print(mpaa)
        except:
            print("CHECK " + movie + " ON REELGOOD")
    try: 
        # Get Rotten Tomatoes via google 
        movies_goog = requests.get("https://www.google.com/search?q=" + "+".join((movie + " " + year).split()))
        goog_soup = BeautifulSoup(movies_goog.content, 'html.parser')
        rt_link = (goog_soup.select("a[href*=rottentomatoes]")[1]["href"]).split("&")[0][7:]
        if ("/s01" in rt_link):
            rt_link = rt_link[:len(rt_link)-4]
        movies_rt = requests.get(rt_link)
        rt_soup = BeautifulSoup(movies_rt.content, 'html.parser')
        try: 
            rt = rt_soup.find("div", {"id": "topSection"}).find("score-board", {"class": "scoreboard"})["tomatometerscore"]
            rt = rt+ "%"
        except:
            rt = rt_soup.find("div", {"id": "topSection"}).find("span", {"class": "mop-ratings-wrap__percentage"}).text.strip()
        print(rt)
    except:
        print(movie + " NOT ON ROTTEN TOMATOES")

    print("!!!!!!!!!!!!!!!!!!!!!!!!!") 

    # Edit on admin

    edit = driver.find_element_by_xpath("/html/body/div/main/header/div/a")
    edit.click()

    # Fill rating

    try: 
        if ((mpaa == "Rated: All (G)") or (mpaa == "Rated: All (TV-G)")):
            driver.find_element_by_xpath("/html/body/div/main/section/form/div[6]/div[2]/select/option[2]").click()
        elif ((mpaa == "Rated: 7+ (TV-PG)") or (mpaa == "Rated: 7+ (PG)")):
            driver.find_element_by_xpath("/html/body/div/main/section/form/div[6]/div[2]/select/option[3]").click()
        elif ((mpaa == "Rated: 13+ (PG-13)") or (mpaa == "Rated: 13+ (TV-MA)")):
            driver.find_element_by_xpath("/html/body/div/main/section/form/div[6]/div[2]/select/option[4]").click()
        elif (mpaa == "Rated: 14+ (TV-14)" or mpaa == "Rated: 14+"):
            driver.find_element_by_xpath("/html/body/div/main/section/form/div[6]/div[2]/select/option[5]").click()
        elif ((mpaa == "Rated: 16+ (TV-MA)") or mpaa == "Rated: 16+"):
            driver.find_element_by_xpath("/html/body/div/main/section/form/div[6]/div[2]/select/option[6]").click()
        elif ((mpaa == "Rated: 18+ (R)")or (mpaa == "Rated: 18+ (TV-MA)")):
            driver.find_element_by_xpath("/html/body/div/main/section/form/div[6]/div[2]/select/option[7]").click()
    except:
        pass 

    # Fill imdb
    try: 
        imdb_fill = driver.find_element_by_id("show_score_imdb")
        imdb_fill.send_keys(str(imdb))
    except:
        pass
    
    # Fill rotten tomatoes
    try:
        if(len(rt) > 1): 
            rt_fill = driver.find_element_by_id("show_score_rotten_tomatoes")
            rt_fill.send_keys(str(rt))
    except:
        pass

    # Update and close 
    driver.find_element_by_name("commit").click()
    driver.back()
    driver.back()
    driver.back()
    driver.refresh()