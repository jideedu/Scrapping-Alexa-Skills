from configparser import ConfigParser
from selenium.webdriver.firefox.options import Options
import time
from datetime import date
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import urllib.request
import re
import json
import sys,os
from bs4.element import Comment,Tag

def login(loginwebsite, email, password, driver):
    '''
    this function sets up the login credentials and waits for the user to input
    the OTP code to login. 

    returns True if all ok, False if exception or error
    '''
    try:
        driver.get(loginwebsite); time.sleep(3) # Let the user actually see something!
        
        #login website
        email_el = driver.find_element_by_id('ap_email')
        email_el.send_keys(email); time.sleep(1)
        driver.find_element_by_id('continue').click(); time.sleep(2)

        passw_el = driver.find_element_by_id('ap_password')
        passw_el.send_keys(password); time.sleep(10)
        driver.find_element_by_id('signInSubmit').click(); time.sleep(2)

        #OTP website, select email option
        try:
            notification = driver.find_element_by_id('resend-approval-alert')
            count = 0
            #ask user to input OTP from email
            print('>>An email from Amazon.co.uk has been sent to {}. Please open the email, and respond to the latest Amazon notification confirmation.'.format(email))
            while ((notification != None) and (count < 10)):
                count = count +1
                print('please respond to the notification')
                time.sleep(10)
                notification = driver.find_element_by_id('resend-approval-alert')     
                                           
        except Exception as e:
            #ugly catch for when Amazon does not show notification confirmation website
            print('>>An error occurred, either: (1) OTP screen was not shown by Amazon, or (2) There was an error with the OTP code. Either way, we will try to proceed.')

        try:
            driver.find_element_by_class_name('a-link-normal cvf-widget-btn-val cvf-widget-link-claim-collect-skip cvf-widget-link-disable-target').click()
        except:
            pass
    
        return True
        
    except Exception as e:
        print('[!] There was an exception when logging {}'.format(e))
        return False

def text_from_html(html_page):
    soup = bs(html_page, "lxml")
    text = soup.find_all(text=True)
    output = ''
    blacklist = ['[document]', 'noscript', 'header','html','meta','head', 'input', 'script', 'style']
    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t.strip())
    #print(output)
    return output

def category_finder(market, MarketLink,  folder):
    if os.path.exists(folder + '//category_links_'+ market):
      os.remove(folder + '//category_links_'+ market)
      print('category file successfully removed')
    else:
      print("The file does not exist")

    #searching skills by categories
    SkillHomePage = {
    'US': MarketLink + '/alexa-skills/b/?ie=UTF8&node=13727921011&ref_=topnav_storetab_a2s',
    'UK': MarketLink + '/b/?ie=UTF8&node=10068517031&ref_=topnav_storetab_a2s',
    'DE': MarketLink + '/b?ie=UTF8&node=10068460031',
    'CA': MarketLink + '/b/?ie=UTF8&node=16286269011&ref_=topnav_storetab_a2s',
    'AU': MarketLink + '/Alexa-Skills/b/?ie=UTF8&node=4931595051&ref_=topnav_storetab_a2s',
    'JP': MarketLink + '/alexa-skills/b/ref=topnav_storetab_a2s?ie=UTF8&node=4788676051',
    'FR': MarketLink + '/b/?ie=UTF8&node=13944548031&ref_=topnav_storetab_a2s',
    'IN': MarketLink + '/b/?ie=UTF8&node=11928183031&ref_=topnav_storetab_a2s',
    'IT': MarketLink + '/b/?ie=UTF8&node=13944605031&ref_=topnav_storetab_a2s',
    'ES': MarketLink + '/b/?ie=UTF8&node=13944662031&ref_=topnav_storetab_a2s',
    'MX': MarketLink + '/b/?ie=UTF8&node=17553254011&ref_=topnav_storetab_a2s'
    }
    try:
        os.mkdir(folder)
    except:
        print("creating folder error")
    
    cat_list=[]
    while (cat_list ==[]):
        ##Get the SkillHomePage
        driver.get(SkillHomePage[market])
        time.sleep(2)
        page = driver.page_source
        #print(page)
        soup = bs(page, "html.parser")
        cat_list1 = soup.findAll("a", attrs={"class": "a-link-normal s-navigation-item"})
        cat_list2 = soup.findAll("a", attrs={"class": "a-color-base a-link-normal"})

        if len(cat_list1) > len(cat_list2):
            cat_list = cat_list1
        else:
            cat_list = cat_list2

    for element in cat_list:
        category_link = (element['href'])
        #print(category_link)
        with open(folder + '//category_links_'+ market, 'a+')as cat:
            cat.write(category_link + "\n")
    print("Categories Extracted")


def Get_Skill():
    c = ''
    #Click the see all the result link
    try:
        driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/a/span').click()
    except:
        try:
            driver.find_element_by_class_name('a-size-medium a-color-link a-text-bold').click()
        except:
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/div/div/a/span').click() 
            except:
                try:
                    driver.find_element_by_xpath('//*[@id=/"a-page/"]/div[2]/div[2]/div[1]/div[2]/div[2]/div/div/a/span').click()
                except:
                    print('No all the result link found')
                    pass

    #Amazon only allow access to 400 pages per category
    #time.sleep(10)            
    for i in range(400):
        print('*****LOADING PAGE {}'.format(i+1))
        
        #time.sleep(5) #use 5sec for review
        page = driver.page_source
        soup = bs(page, "html.parser")

        #getting current url
        url = driver.current_url
        #this break the loop when the same URL is return
        if c == url:
            break
        c = url
        links = soup.find_all("a", attrs={"class": "a-link-normal s-no-outline"})
        for link in links:
            Skill_Url = (link['href'])
            try:
                Skill_Url = Skill_Url.replace(MarketLink,"")
                Skill_Url = MarketLink + Skill_Url
                SkillDetails(Skill_Url)
                #time.sleep(3)
            except Exception:
                pass
            
            
        #getting next page
        driver.get(url)
        try:
            driver.find_element_by_class_name('a-last').click()
        except Exception:
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/div[2]/div/span[3]/div[2]/div[17]/span/div/div/ul/li[7]/a').click()
            except Exception:
                try: 
                    driver.find_element_by_id('a-normal').click()     
                except Exception:
                    try:
                        driver.find_element_by_id('pagnNextString').click()     
                    except Exception:
                        print('Unable to Click on next page')
                        pass
                       
        
def SkillDetails(Skill_Url):
    try:
        driver.get(Skill_Url)
    except Exception:
        pass
    page = driver.page_source
    soup = bs(page, "html.parser")
    skills_details = dict()

    #getting the skill ID
    skill_id = re.search(r"\b[B]+[0-9]+(?:[A-Z0-9]+/)+", Skill_Url).group()
    skill_id = skill_id.replace('/',"")

    #getting the skill name
    try:
        skill_name= soup.find("h1", attrs={"class": "a2s-title-content"})
        skill_name = skill_name.get_text().strip()
    except:
        try:
            skill_name= soup.find("h1", attrs={"class": "a2s-title-content"})
            skill_name = skill_name.get_text()
        except:
            pass
        
    #getting the invocation name
    try:
        invocation_name= soup.findAll("span", attrs={"class": "a-text-bold"})
        invocation_name = invocation_name[1].get_text().strip()
    except:
        try:
            invocation_name= soup.find("span", attrs={"class": "a-list-item"})
            invocation_name = invocation_name.get_text().strip()
        except:
            pass
    print(invocation_name)

    #getting the skill_developer    		
    try:
        skill_developer= soup.find("span", attrs={"class": "a-size-base a-color-secondary"})
        skill_developer = skill_developer.get_text().strip()
        print ("skill_developer extracted for " + skill_name)
    except Exception:
        skill_developer= ""
        
    #getting the permission
    #allpermlink = driver.find_elements_by_class_name('a2s-permissions-list-item')
    #permissions_requested = [i.text for i in allpermlink]
    #privacy_link = driver.find_element_by_partial_link_text('Developer Privacy Policy').get_attribute("href")
            
    try:
        b22 = soup.findAll("li", attrs={"class": "a2s-permissions-list-item"})
        skill_permission =list()
        for b in b22:
            skill_permission.append(b.get_text().strip())
        print("permission extracted for " + skill_name)
    except:
        pass

    #Checking if account linking required
    try:
        account_linking = soup.find("span", attrs={"id": "a2s-skill-account-link-msg"})
        account_linking = account_linking.get_text().strip()
        print ("account_linking extracted for " + skill_name)
    except:
        account_linking = ""
        
    #getting the In_skill_purchase
    try:     
        In_skill_purchase = soup.find("p", attrs={"class": "a-text-left a-size-small"})
        In_skill_purchase = In_skill_purchase.get_text().strip()
        print ("In_skill_purchase extracted for" + skill_name)
    except Exception:
        try:
            In_skill_purchase = soup.find("p", attrs={"class": "a-text-left a-size-small"})
            In_skill_purchase = In_skill_purchase
            print ("In_skill_purchase extracted for " + skill_name)
        except Exception:
            pass
        
    #getting the skill review
    try:
        skill_review = soup.find("h2", attrs={"data-hook": "total-review-count"})
        skill_review = skill_review.get_text().strip()

    except Exception:
        try:
            skill_review= soup.find("span", attrs={"data-hook": "total-review-count"})
            skill_review = skill_review.get_text()
            print ("skill_review extracted for " + skill_name)
        except Exception:
            pass

    #getting the skills category
    try:
        cat= soup.findAll("a", attrs={"class": "a-link-normal a-color-tertiary"})

    except Exception:
        try:
            cat= soup.findAll("a", attrs={"class": "a-size-small a-color-base"})
        except Exception:
            pass
    if len(cat)>0:
        try:
            cat1 = cat[1].get_text().strip()
            cat2 = cat[2].get_text().strip()
            skills_details['Main Category']= cat1
            skills_details['SubCategory']= cat2
            print ("skills category extracted for " + skill_name)
        except Exception:
            try:
                cat1 = cat[1].get_text().strip()
                skills_details['Main Category']= cat1
                skills_details['SubCategory']= cat1
                print ("skills category extracted for " + skill_name)
            except Exception:
                skills_details['SubCategory']= ""
                   
    #getting the skill rating   
    try:   
        skill_rating= soup.find("i", attrs={"data-hook": "average-star-rating"})
        skill_rating = skill_rating.get_text().strip()
        print ("skill_rating extracted")
    except Exception:
        try:   
            skill_rating= soup.find("h2", attrs={"data-hook": "total-rating-count"})
            skill_rating = skill_rating.get_text().strip()
            print ("skill_rating extracted for " + skill_name)
        except Exception:
            skill_rating = ""

    #getting the Total customer that rate the skill
    try:   
        Total_customer_that_rate_the_skill= soup.findAll("span", attrs={"class": "a-size-small a-color-link a2s-review-star-count"})
        Total_customer_that_rate_the_skill = Total_customer_that_rate_the_skill[0].get_text().strip()
        print ("Total_customer_that_rate_the_skill extracted for " + skill_name)
        
    except Exception:
        Total_customer_that_rate_the_skill = ""
                
    #getting the Total_Customers_Reviews
    try:
        Total_Customers_Reviews= soup.find("span", attrs={"data-hook": "top-customer-reviews-title"})
        Total_Customers_Reviews = Total_Customers_Reviews.get_text().strip()
        print ("Total_Customers_Reviews extracted for " + skill_name)
    except Exception:
        try:
            Total_Customers_Reviews= soup.find("span", attrs={"class": "arp-rating-out-of-text a-color-base"})
            Total_Customers_Reviews = Total_Customers_Reviews.get_text().strip()
            print ("Total_Customers_Reviews extracted for " + skill_name)
        except Exception:
            Total_Customers_Reviews = ""
        
    #getting the cost
    try:     
        cost_of_skill = soup.find("p", attrs={"class": "a-spacing-none a-text-left a-size-medium a-color-price"})
        cost_of_skill = cost_of_skill.get_text().strip()
    except Exception:
        try:
            cost_of_skill = soup.find("p", attrs={"class": "a-spacing-none a-text-left a-size-medium a-color-price"})
            cost_of_skill = cost_of_skill
        except Exception:
            pass

    #get the skill description
    skill_description = soup.find("div", attrs={"id": "a2s-description"})
    skill_description= skill_description.get_text("\n").strip()
        
    #GET  INVOCATION Utterances
    invocation_utterances= soup.findAll("div", attrs={"class": "a2s-utterance-box a2s-bubble"})
    invocation_utterance =list()
    for a in invocation_utterances:
        #print('{}\n'.format(a.get_text().strip()))
        invocation_utterance.append(a.get_text().strip())
        #mymy.write('{}\n'.format(a.get_text().strip()))

    if skill_name != "":            
        skills_details['Name']= skill_name
        skills_details['Skill_ID'] = skill_id
        skills_details['Developer']= skill_developer
        skills_details['Skill_permission'] = skill_permission
        skills_details['Account_linking'] = account_linking
        skills_details['Sample_Invocation_Utterances']= invocation_utterance
        #skills_details['Invocation_Name']= invocation_name
        skills_details['Review_Count']= skill_review
        skills_details['Rating']= skill_rating
        skills_details['Total_customer_that_rate_the_skill'] = Total_customer_that_rate_the_skill
        skills_details['Total_Customers_Reviews'] = Total_Customers_Reviews
        skills_details['Cost'] = cost_of_skill
        skills_details['In_skill_purchase'] = In_skill_purchase
        skills_details['Skill_description'] = skill_description
        skills_details['Skill_link'] = driver.current_url
            
    #GETting DYNAMIC CONTENT
    a=list()
    a = soup.findAll("a", attrs={"rel": "noopener"})
    #a = soup.findAll("a", attrs={"target": "_blank"})

    #Checking to see if privacy_link and developer_link exist
    if len(a)> 0:
        try:
            a1 = a[0]
            a2 = a[1]
            privacy_policy = (a1['href'])
            Terms_of_use = (a2['href'])
            skills_details['privacy_policy']= privacy_policy
            skills_details['Terms_of_use']= Terms_of_use
            
        except Exception:
            a1 = a[0]
            privacy_policy = (a1['href'])
            skills_details['privacy_policy']= privacy_policy
            skills_details['Terms_of_use']= ""          
    else:
        skills_details['privacy_policy']= ""
        skills_details['Terms_of_use']= ""
        skills_details['privacy_policy_doc']= ""

    if (privacy_policy != "") and (len(skill_permission)>0):
        driver.get(privacy_policy)
        page = driver.page_source.lower()
        cleanpage = text_from_html(page)
        skills_details['privacy_policy_doc']= cleanpage

    #Loading all review page
    try:
        driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[2]/div/div[2]/span[3]/div/div/div[4]/div[2]/a').click()
        print ("Loading all review page for " + skill_name)
        time.sleep(2)
    except:
        try:
            driver.find_element_by_class_name('a-link-emphasis a-text-bold').click()
            print ("Loading2 all review page for " + skill_name)
        except:
            print(" No review to Click on for " + skill_name)
            pass
    try:
        #Getting Negative Reviews
        
        all_spans = driver.find_elements_by_xpath("//a[@class='a-size-base a-link-normal see-all']")
        Total_neg_words = all_spans[1].text  
        time.sleep(3)
        print (Total_neg_words)
        neg_split = Total_neg_words.split()
        Total_neg_review = neg_split[2]
        if "," in Total_neg_review:
            Total_neg_review = Total_neg_review.replace(",", "")
        actual_reviews = int(Total_neg_review)
        skills_details['Total Negative Reviews'] = int(Total_neg_review)
        print('total negative review(s) for {} is {}'. format(skill_name, Total_neg_review))
        all_spans[1].click()
        print ("Loading all negative reviews for " + skill_name)


        xxx = driver.current_url       
        #No of review page to open
        try:
            review_page = (-(-actual_reviews // 10))
            print("Pages to load is {} for {} skill". format(review_page, skill_name))
        except:
            review_page = 1 ###################################change from 0 to 1 untested

        negative_review = {}
        b = list()
        c = list()

        #TIME INTRODUCE TO AVOID BOT#################   
        for i in range(review_page):
            print('*****LOADING PAGE {} Review for  {}*************************'.format(i+1,skill_name))
            time.sleep(3)
            page2 = driver.page_source
            soup2 = bs(page2, "html.parser")

            #Getting users and comments        
            users = soup2.findAll("span", attrs={"class":"a-profile-name"})
            comments = soup2.findAll("span", attrs={"class":"a-size-base review-text review-text-content"})
            users= users[2:]
        
            #looping though each users and comments
            for index,el in enumerate(comments):
                time.sleep(1)
                user = users[index].get_text().strip()
                comment = comments[index].get_text().strip()
                negative_review[user] = comment
                
            #Get Next Review Page
            try:
                driver.find_element_by_class_name('a-last').click()    
            except:         
                pass  # or you could use 'continue' 

        #Adding the result to the skill details dictionary
        skills_details['Negative Reviews'] = negative_review
    except:
        pass

    d4 = date.today().strftime("%b-%d-%Y")
    #dump all what you have in the skill details dictionary to a file
    with open(folder + '//file_'+ market + '_' + d4 + '.json', 'a+') as fp:
        json.dump(skills_details, fp)
        fp.write('\n')
    
def subcategory(market, MarketLink, folder):
    seen_category = list()
    if os.path.exists(folder + '//subcategory_links_' + market):
        os.remove(folder + '//subcategory_links_' + market)
        print('successfully remove subcategory file')
    else:
        print("The file does not exist")
        
    with open(folder + '//category_links_'+ market, 'r')as pick:
        for index, category in enumerate(pick):    
            if category not in seen_category :
                seen_category.append(category)
    
                ##Get the SubCategoryPage    
                driver.get(MarketLink + category)

                #Extracting the sub Caegeory
                page = driver.page_source
                soup = bs(page, "html.parser")
                cat_list = soup.findAll("a", attrs={"class": "a-link-normal s-navigation-item"})
                if cat_list ==[]:
                    cat_list = soup.findAll("a", attrs={"class": "a-color-base a-link-normal"}) 
                for element in cat_list: 
                    categorysub_link = (element['href'])
                    if categorysub_link not in seen_category:
                        seen_category.append(categorysub_link)

    for link in seen_category:
        #we need to filter out the Main category
        if 'ex_n_1' not in link:    
            with open(folder + '//subcategory_links_' + market, 'a+')as cat2:     
                cat2.write(link.strip() + "\n" )
    print("SubCategories Extracted")
                        

folder = 'Output'
#market = 'US'   #Specify the market to crawl
#if (True):
markets = ['US', 'UK', 'CA', 'AU', 'IN', 'MX', 'ES', 'IT', 'FR', 'DE', 'JP']
for market in markets:
    
    chromedriverpath = "chromedriver_win32/chromedriver.exe"
    firefoxdriverpath = "Firefoxdriver_win32/geckodriver.exe"

    MarketLinks = {   
            'US':"https://www.amazon.com",
            'UK': "https://www.amazon.co.uk",
            'DE':"https://www.amazon.de",
            'CA' :"https://www.amazon.ca",
            'AU' :"https://www.amazon.com.au",
            'JP' :"https://www.amazon.co.jp",
            'FR' :"https://www.amazon.fr",
            'IN' :"https://www.amazon.in",
            'IT' :"https://www.amazon.it",
            'MX' :"https://www.amazon.com.mx",
            'ES' :"https://www.amazon.es"
            }
    MarketLink = MarketLinks[market]

    LoginLinks = {   
            'US': MarketLink + "/ap/signin?_encoding=UTF8&ignoreAuthState=1&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin&switch_account=",
            'UK': MarketLink + "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.co.uk%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=gbflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&",
            "DE": MarketLink + "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.de%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=deflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&",
            "CA" : MarketLink + "/ap/signin?_encoding=UTF8&openid.assoc_handle=caflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.ca%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26action%3Dsign-out%26path%3D%252Fgp%252Fyourstore%252Fhome%26ref_%3Dnav_AccountFlyout_signout%26signIn%3D1%26useRedirectOnSuccess%3D1",
            "AU" : MarketLink + "/ap/signin?_encoding=UTF8&openid.assoc_handle=auflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com.au%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26action%3Dsign-out%26path%3D%252Fgp%252Fyourstore%252Fhome%26ref_%3Dnav_AccountFlyout_signout%26signIn%3D1%26useRedirectOnSuccess%3D1",
            "JP" : MarketLink + "/-/en/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.co.jp%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=jpflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&",
            "FR" : MarketLink + "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.fr%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=frflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&",
            "IN" : MarketLink + "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&",
            "IT" : MarketLink + "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.it%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=itflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&",
            "MX" : MarketLink + "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com.mx%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=mxflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&",
            "ES" : MarketLink + "/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.es%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=esflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
            }
    LoginLink = LoginLinks[market]

#Add your Amazon email address and pssword
    email = ""
    password = ""

    #Create a new instance of the Mozilla driver
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, executable_path=firefoxdriverpath)
    #driver = webdriver.Firefox(executable_path=firefoxdriverpath)
    #driver = webdriver.Chrome(options=options, executable_path = chromedriverpath)

    #only enable this to get category_links : Must be run first
    category_finder(market, MarketLink, folder)

    #Enable only after commenting category finder
    subcategory(market,MarketLink, folder)

    #Calling Login function
    login(LoginLink, email, password, driver)


    with open(folder + '//subcategory_links_' + market, 'r')as pick:
        for line in pick:            
            line = line.replace(MarketLink,"")
            line = MarketLink + line
            driver.get(line)
            try:
                data = Get_Skill()
            except Exception:
                pass
